# services/grading_service.py

import os
import json
import fitz  # PyMuPDF
import openai
from dotenv import load_dotenv
from fastapi import UploadFile
from typing import List, Optional
import traceback
from fastapi.responses import JSONResponse

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

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
PROJECTS_DIR = "projects"
os.makedirs(PROJECTS_DIR, exist_ok=True)

def extract_text_from_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        text = "".join(page.get_text() for page in doc)
        return text
    except Exception as e:
        print("❌ PDF error:", e)
        return ""

async def handle_project_creation(
    project_id: str,
    project_name: str,
    subject: str,
    num_questions: int,
    num_tests: int,
    project_type: str,
    expected_average: Optional[int],
    solution_file: Optional[UploadFile],
    test_files: List[UploadFile]
):
    try:
        # 🔹 יצירת תיקיות לפרויקט
        project_path = os.path.join(PROJECTS_DIR, f"{project_name}_{project_id}")
        os.makedirs(project_path, exist_ok=True)
        tests_dir = os.path.join(project_path, "tests")
        os.makedirs(tests_dir, exist_ok=True)

        # 🔹 שמירת פתרון ובניית טקסט
        solution_text = ""
        if solution_file:
            solution_path = os.path.join(project_path, f"solution_{solution_file.filename}")
            with open(solution_path, "wb") as f:
                f.write(await solution_file.read())
            solution_text = extract_text_from_pdf(solution_path)

        # 🔹 שמירת מבחנים ויצירת טקסטים
        student_texts = []
        for idx, test_file in enumerate(test_files):
            test_path = os.path.join(tests_dir, f"test_{idx+1}_{test_file.filename}")
            with open(test_path, "wb") as f:
                f.write(await test_file.read())
            student_texts.append((test_file.filename, extract_text_from_pdf(test_path)))

        # 🔹 בניית פרומפט לפי סוג מבחן
        if project_type == "open":
            full_prompt = build_open_test_prompt(subject, num_questions, solution_text, expected_average, student_texts)
        elif project_type == "multichoice":
            full_prompt = build_multichoice_prompt(subject, num_questions, solution_text, expected_average, student_texts)
        elif project_type == "homework":
            full_prompt = build_homework_prompt(subject, num_questions, solution_text, expected_average, student_texts)
        else:
            return JSONResponse(status_code=400, content={"error": "Invalid project_type"})

        # 🔹 שמירת הפרומפט
        with open(os.path.join(project_path, "prompt.txt"), "w", encoding="utf-8") as f:
            f.write(full_prompt)

        # 🔹 קריאה ל־OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.0,
            max_tokens=4000
        )
        gpt_output = response['choices'][0]['message']['content'].strip()

        # 🔹 המרה ל־JSON
        try:
            results = json.loads(gpt_output)
        except json.JSONDecodeError:
            print("❌ GPT returned invalid JSON:\n", gpt_output)
            return JSONResponse(status_code=500, content={"error": "Invalid GPT output."})

        # 🔹 שמירת התוצאות
        with open(os.path.join(project_path, "results.json"), "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        # 🔹 חישובי סטטיסטיקה
        scores = [student["overall_score"] for student in results]

        stats = {
            "average": calculate_average(scores),
            "median": calculate_median(scores),
            "std_dev": calculate_std_dev(scores),
            "grade_distribution": calculate_grade_distribution(scores),
        }

        return {
            "project_name": project_name,
            "project_id": project_id,
            "num_tests": num_tests,
            "expected_average": expected_average,
            "results": results,
            "stats": stats
        }

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})