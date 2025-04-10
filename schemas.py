from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    name: str
    age: int
    gender: str
    weight: float
    height: float
    fitness_level: str
    goal: str
    equipment: str
    workout_duration: int
    health_constraints: Optional[str] = None

class WorkoutResponse(BaseModel):
    message: str
    plan: List[dict]

class WorkoutPlan(BaseModel):
    exercise: str
    sets: int
