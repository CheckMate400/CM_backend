# services/project_service.py

import os
import json
from models.project import ProjectCreate

PROJECTS_DIR = "projects"
os.makedirs(PROJECTS_DIR, exist_ok=True)

def handle_create_project(data: ProjectCreate):
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
