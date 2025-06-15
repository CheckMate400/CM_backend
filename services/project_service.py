# services/project_service.py

import os
import json
from models.project import ProjectCreateRequest

PROJECTS_DIR = "projects"
os.makedirs(PROJECTS_DIR, exist_ok=True)

def handle_create_project(data: ProjectCreateRequest):
    folder_name = f"{data.project_name}_{data.subject}".replace(" ", "_")
    folder_path = os.path.join(PROJECTS_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    metadata = {
        "name": data.project_name,
        "subject": data.subject,
        "num_questions": data.num_questions
    }

    with open(os.path.join(folder_path, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return {"message": "✅ Project created", "folder": folder_name}


def get_all_projects():
    project_list = []

    if not os.path.exists(PROJECTS_DIR):
        return []

    for folder_name in os.listdir(PROJECTS_DIR):
        folder_path = os.path.join(PROJECTS_DIR, folder_name)
        meta_path = os.path.join(folder_path, "meta.json")
        results_path = os.path.join(folder_path, "results.json")

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            with open(results_path, "r", encoding="utf-8") as f:
                results = json.load(f)

            scores = [s["overall_score"] for s in results]
            stats = {
                "average": calculate_average(scores),
                "median": calculate_median(scores),
                "std_dev": calculate_std_dev(scores),
                "grade_distribution": calculate_grade_distribution(scores),
            }

            project_list.append({
                "project_id": folder_name,
                "project_name": meta["name"],
                "subject": meta["subject"],
                "num_questions": meta["num_questions"],
                "num_tests": len(scores),
                "stats": stats,
            })

        except Exception as e:
            print(f"❌ Error loading project {folder_name}:", e)

    return project_list
