# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import projects

app = FastAPI()

# CORS – תקשורת עם ה-Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # אפשר להחליף לדומיין ספציפי בפרודקשן
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# חיבור הנתיבים
app.include_router(projects.router, prefix="/projects", tags=["Projects"])

# בדיקה
@app.get("/")
def root():
    return {"status": "✅ CheckMate backend is running"}
