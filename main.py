from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import fitz  # PyMuPDF
import uuid
import os
import json
import openai
from dotenv import load_dotenv

from utils.statistics import (
    calculate_average,
    calculate_grade_distribution,
    calculate_median,
    calculate_std_dev,
)
from prompt_builder.grading_prompts import (
    build_open_test_prompt,
    build_multichoice_prompt,
    build_homework_prompt,
)

# Load environment variables from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
print("\n✅ API key loaded\n" if openai.api_key else "\n❌ API key missing\n")

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Projects directory setup
PROJECTS_DIR = "projects"
os.makedirs(PROJECTS_DIR, exist_ok=True)

# --------- Helpers ---------

def extract_text_from_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        text = "".join(page.get_text() for page in doc)
        return text
    except Exception as e:
        print("❌ PDF error:", e)
        return ""

# --------- Main Route ---------

@app.post("/create_project/")
async def create_project(
    project_name: str = Form(...),
    subject: str = Form(...),
    num_questions: int = Form(...),
    num_tests: int = Form(...),
    project_type: str = Form(...),  # "open", "multichoice", or "homework"
    expected_average: Optional[int] = Form(None),
    solution_file: Optional[UploadFile] = File(None),
    test_files: List[UploadFile] = File(...)
):
    # Setup project folders
    project_id = str(uuid.uuid4())
    project_path = os.path.join(PROJECTS_DIR, f"{project_name}_{project_id}")
    os.makedirs(project_path, exist_ok=True)
    tests_dir = os.path.join(project_path, "tests")
    os.makedirs(tests_dir, exist_ok=True)

    # Save and extract solution
    solution_text = ""
    if solution_file:
        solution_path = os.path.join(project_path, f"solution_{solution_file.filename}")
        with open(solution_path, "wb") as f:
            f.write(await solution_file.read())
        solution_text = extract_text_from_pdf(solution_path)

    # Save and extract student submissions
    student_texts = []
    for idx, test_file in enumerate(test_files):
        test_path = os.path.join(tests_dir, f"test_{idx+1}_{test_file.filename}")
        with open(test_path, "wb") as f:
            f.write(await test_file.read())
        student_texts.append((test_file.filename, extract_text_from_pdf(test_path)))

    # Build prompt based on project_type
    if project_type == "open":
        full_prompt = build_open_test_prompt(subject, num_questions, solution_text, expected_average, student_texts)
    elif project_type == "multichoice":
        full_prompt = build_multichoice_prompt(subject, num_questions, solution_text, expected_average, student_texts)
    elif project_type == "homework":
        full_prompt = build_homework_prompt(subject, num_questions, solution_text, expected_average, student_texts)
    else:
        return JSONResponse(status_code=400, content={"error": "Invalid project_type"})

    # Save prompt to project folder
    with open(os.path.join(project_path, "prompt.txt"), "w", encoding="utf-8") as f:
        f.write(full_prompt)

    # GPT Call
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.0,
            max_tokens=4000
        )
        gpt_output = response['choices'][0]['message']['content'].strip()

        try:
            results = json.loads(gpt_output)
        except json.JSONDecodeError:
            print("❌ GPT returned invalid JSON:\n", gpt_output)
            return JSONResponse(status_code=500, content={"error": "Invalid GPT output."})

        # Save results
        with open(os.path.join(project_path, "results.json"), "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        scores = [student["overall_score"] for student in results]

        stats = {
            "average": calculate_average(scores),
            "median": calculate_median(scores),
            "std_dev": calculate_std_dev(scores),
            "grade_distribution": calculate_grade_distribution(scores),
        }

        return JSONResponse(content={
            "project_name": project_name,
            "project_id": project_id,
            "num_tests": num_tests,
            "expected_average": expected_average,
            "results": results,
            "stats": stats
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
