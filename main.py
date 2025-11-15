import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents

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

# Seed curriculum (idempotent)
@app.post("/api/seed")
def seed():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    topics_count = db["topic"].count_documents({})
    if topics_count > 0:
        return {"status": "ok", "message": "Already seeded"}

    def topic(title: str, slug: str, description: str, order: int) -> str:
        return create_document("topic", {
            "title": title,
            "slug": slug,
            "description": description,
            "order": order
        })

    def lesson(topic_id: str, title: str, slug: str, content: str, order: int, level: str = "beginner") -> str:
        return create_document("lesson", {
            "topic_id": topic_id,
            "title": title,
            "slug": slug,
            "content": content,
            "order": order,
            "level": level
        })

    def mcq(lesson_id: str, question: str, options, answer: str, explanation: str, order: int):
        return create_document("exercise", {
            "lesson_id": lesson_id,
            "question": question,
            "type": "mcq",
            "options": options,
            "answer": answer,
            "explanation": explanation,
            "order": order
        })

    def textq(lesson_id: str, question: str, answer: str, explanation: str, order: int):
        return create_document("exercise", {
            "lesson_id": lesson_id,
            "question": question,
            "type": "text",
            "answer": answer,
            "explanation": explanation,
            "order": order
        })

    # Topics
    t_basics = topic("C# Basics", "csharp-basics", "Start with characters, strings, variables, and types.", 0)
    t_types = topic("Types & Variables", "types-variables", "Value vs reference types, var, constants.", 1)
    t_control = topic("Control Flow", "control-flow", "if/else, switch, loops.", 2)
    t_methods = topic("Methods", "methods", "Parameters, return values, overloading.", 3)
    t_arrays = topic("Arrays & Collections", "arrays-collections", "Arrays, List<T>, Dictionary<TKey,TValue>.", 4)
    t_oop = topic("Object-Oriented Programming", "oop", "Classes, objects, inheritance, interfaces.", 5)
    t_ex = topic("Exceptions", "exceptions", "try/catch, custom exceptions, finally.", 6)
    t_linq = topic("LINQ", "linq", "Querying collections with LINQ.", 7)
    t_async = topic("Async & Await", "async-await", "Tasks, async methods, await.", 8)

    # Lessons and exercises (representative sample for each topic)
    l_char = lesson(t_basics, "Characters in C#", "characters", "# char in C#\nUse single quotes: char c = 'A';\nUnicode supported.\n", 0)
    l_string = lesson(t_basics, "Strings in C#", "strings", "# string in C#\nImmutable sequences of characters.\nInterpolation: $\"Hello {name}\"\n", 1)
    mcq(l_char, "Which literal defines a char?", [
        {"key": "A", "text": "'A'"},
        {"key": "B", "text": "\"A\""},
        {"key": "C", "text": "A"}
    ], "A", "char uses single quotes in C#.", 0)
    mcq(l_string, "What is the string interpolation prefix?", [
        {"key": "A", "text": "$"},
        {"key": "B", "text": "@"},
        {"key": "C", "text": "#"}
    ], "A", "Use $ before string literal for interpolation.", 0)

    l_types = lesson(t_types, "Value vs Reference Types", "value-vs-reference", "# Types\nint, double, bool are value types.\nstring, arrays, class instances are reference types.\n", 0)
    textq(l_types, "Is string a value or reference type? Answer with 'value' or 'reference'.", "reference", "string is a reference type in C#.", 0)

    l_control = lesson(t_control, "if/else and switch", "if-switch", "# Control Flow\nUse if/else and switch to branch logic.\n", 0)
    textq(l_control, "What keyword starts a switch block?", "switch", "A switch statement starts with the 'switch' keyword.", 0)

    l_methods = lesson(t_methods, "Methods & Parameters", "methods-params", "# Methods\nMethods can be static or instance.\nPass by value by default; use 'ref'/'out' for by-ref.\n", 0)
    textq(l_methods, "What keyword passes an argument by reference (short form)?", "ref", "Use 'ref' to pass by reference; 'out' for uninitialized output.", 0)

    l_arrays = lesson(t_arrays, "Arrays & Lists", "arrays-lists", "# Arrays & Collections\nint[] arr = new int[3];\nvar list = new List<int>();\n", 0)
    textq(l_arrays, "Write the type name for a growable integer collection in generics.", "List<int>", "List<int> is a generic growable list.", 0)

    l_oop = lesson(t_oop, "Classes & Inheritance", "classes-inheritance", "# OOP\nclass Animal { }\nclass Dog : Animal { }\nInterfaces use ': IInterface'.\n", 0)
    textq(l_oop, "Fill in: class Dog : ____ { } (base class is Animal)", "Animal", "Inheritance uses ':' followed by the base class.", 0)

    l_ex = lesson(t_ex, "Handling Exceptions", "handling-exceptions", "# Exceptions\ntry { ... } catch (Exception ex) { ... } finally { ... }\n", 0)
    textq(l_ex, "What block runs regardless of exceptions?", "finally", "The 'finally' block always runs.", 0)

    l_linq = lesson(t_linq, "Intro to LINQ", "intro-linq", "# LINQ\nvar evens = numbers.Where(n => n % 2 == 0);\n", 0)
    textq(l_linq, "LINQ: method to filter elements by predicate?", "Where", "Use .Where(predicate) to filter.", 0)

    l_async = lesson(t_async, "Async & Await", "async-await-lesson", "# Async\nasync Task<int> GetAsync() { await Task.Delay(10); return 1; }\n", 0)
    textq(l_async, "Keyword used before a method to enable awaiting inside it.", "async", "Mark methods with 'async' to use 'await'.", 0)

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
    from database import create_document
    create_document("progress", p.model_dump())
    return {"status": "ok"}
