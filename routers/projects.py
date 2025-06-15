# routers/projects.py

from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import uuid
from services.grading_service import handle_project_creation
from models.project import ProjectCreateRequest

router = APIRouter()

@router.post("/create")
async def create_project_route(
    project_name: str = Form(...),
    subject: str = Form(...),
    num_questions: int = Form(...),
    num_tests: int = Form(...),
    project_type: str = Form(...),  # "open", "multichoice", or "homework"
    expected_average: Optional[int] = Form(None),
    solution_file: Optional[UploadFile] = File(None),
    test_files: List[UploadFile] = File(...)
):
    project_id = str(uuid.uuid4())

    return await handle_project_creation(
        project_id=project_id,
        project_name=project_name,
        subject=subject,
        num_questions=num_questions,
        num_tests=num_tests,
        project_type=project_type,
        expected_average=expected_average,
        solution_file=solution_file,
        test_files=test_files
    )
