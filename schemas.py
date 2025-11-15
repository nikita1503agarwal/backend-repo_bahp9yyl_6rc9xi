"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Learning app schemas for C# curriculum

class Topic(BaseModel):
    """
    Topic collection
    Represents a high-level subject in the C# curriculum (e.g., Variables, Strings, OOP)
    Collection name: "topic"
    """
    title: str = Field(..., description="Topic title")
    slug: str = Field(..., description="URL-friendly identifier")
    description: Optional[str] = Field(None, description="Short description")
    order: int = Field(..., ge=0, description="Display order")

class Lesson(BaseModel):
    """
    Lesson collection
    Represents a single lesson under a topic
    Collection name: "lesson"
    """
    topic_id: str = Field(..., description="Reference to Topic _id (string)")
    title: str = Field(..., description="Lesson title")
    slug: str = Field(..., description="URL-friendly identifier")
    content: str = Field(..., description="Markdown content of the lesson")
    order: int = Field(..., ge=0, description="Display order within topic")
    level: str = Field("beginner", description="beginner | intermediate | advanced")

class ExerciseOption(BaseModel):
    key: str = Field(..., description="Option key like A, B, C, D")
    text: str = Field(..., description="Option text")

class Exercise(BaseModel):
    """
    Exercise collection
    Multiple-choice or small code reading questions attached to a lesson
    Collection name: "exercise"
    """
    lesson_id: str = Field(..., description="Reference to Lesson _id (string)")
    question: str = Field(..., description="Question text")
    type: str = Field("mcq", description="mcq | text")
    options: Optional[List[ExerciseOption]] = Field(None, description="Options for MCQ")
    answer: Optional[str] = Field(None, description="Correct answer key or sample answer for text")
    explanation: Optional[str] = Field(None, description="Explanation of the answer")
    order: int = Field(..., ge=0, description="Display order within lesson")

class Progress(BaseModel):
    """
    Progress collection
    Tracks a user's completion per lesson
    Collection name: "progress"
    """
    user_id: str = Field(..., description="User identifier (client-generated)")
    lesson_id: str = Field(..., description="Lesson id")
    status: str = Field("completed", description="completed | in_progress")
    score: Optional[float] = Field(None, ge=0, le=100, description="Score percentage for exercises")

# Example schemas (left for reference)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
