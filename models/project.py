# models/project.py

from pydantic import BaseModel

class ProjectCreate(BaseModel):
    project_name: str
    subject: str
    num_questions: int
