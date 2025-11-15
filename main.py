import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Topic, Lesson, Exercise, Progress

app = FastAPI(title="C# Learning Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers
class ObjectIdStr(BaseModel):
    id: str

def to_str_id(doc):
    if doc is None:
        return None
    d = {**doc}
    if "_id" in d:
        d["_id"] = str(d["_id"])  # type: ignore
    return d

@app.get("/")
def read_root():
    return {"message": "C# Learning Platform Backend"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Seed minimal curriculum if empty
@app.post("/api/seed")
def seed():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    topics_count = db["topic"].count_documents({})
    if topics_count > 0:
        return {"status": "ok", "message": "Already seeded"}

    # Create Topics
    basics_id = create_document("topic", {
        "title": "C# Basics",
        "slug": "csharp-basics",
        "description": "Start with characters, strings, variables, and types.",
        "order": 0
    })
    oop_id = create_document("topic", {
        "title": "Object-Oriented Programming",
        "slug": "oop",
        "description": "Classes, objects, inheritance, interfaces.",
        "order": 1
    })

    # Lessons under Basics
    lesson_char_id = create_document("lesson", {
        "topic_id": basics_id,
        "title": "Characters in C#",
        "slug": "characters",
        "content": "# char in C#\nUse single quotes: char c = 'A';\nUnicode supported.\n",
        "order": 0,
        "level": "beginner"
    })
    lesson_string_id = create_document("lesson", {
        "topic_id": basics_id,
        "title": "Strings in C#",
        "slug": "strings",
        "content": "# string in C#\nImmutable sequences of characters.\nInterpolation: $\"Hello {name}\"\n",
        "order": 1,
        "level": "beginner"
    })

    # Exercises
    create_document("exercise", {
        "lesson_id": lesson_char_id,
        "question": "Which literal defines a char?",
        "type": "mcq",
        "options": [
            {"key": "A", "text": "'A'"},
            {"key": "B", "text": "\"A\""},
            {"key": "C", "text": "A"}
        ],
        "answer": "A",
        "explanation": "char uses single quotes in C#.",
        "order": 0
    })
    create_document("exercise", {
        "lesson_id": lesson_string_id,
        "question": "What is string interpolation prefix?",
        "type": "mcq",
        "options": [
            {"key": "A", "text": "$"},
            {"key": "B", "text": "@"},
            {"key": "C", "text": "#"}
        ],
        "answer": "A",
        "explanation": "Use $ before string literal for interpolation.",
        "order": 0
    })

    return {"status": "ok", "message": "Seeded"}

# Public APIs
@app.get("/api/topics")
def get_topics():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("topic", {}, None)
    return [to_str_id(d) for d in sorted(docs, key=lambda x: x.get("order", 0))]

@app.get("/api/topics/{topic_id}/lessons")
def get_lessons(topic_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("lesson", {"topic_id": topic_id}, None)
    return [to_str_id(d) for d in sorted(docs, key=lambda x: x.get("order", 0))]

@app.get("/api/lessons/{lesson_id}/exercises")
def get_exercises(lesson_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("exercise", {"lesson_id": lesson_id}, None)
    return [to_str_id(d) for d in sorted(docs, key=lambda x: x.get("order", 0))]

class ProgressIn(BaseModel):
    user_id: str
    lesson_id: str
    status: Optional[str] = "completed"
    score: Optional[float] = None

@app.post("/api/progress")
def set_progress(p: ProgressIn):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    create_document("progress", p.model_dump())
    return {"status": "ok"}
