from pydantic import BaseModel

class ProjectCreateRequest(BaseModel):
    project_name: str
    subject: str
    num_questions: int
    num_tests: int
    project_type: str
    expected_average: int | None = None
