from pydantic import BaseModel
from typing import Optional

# User schema for input
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

# Workout Plan Output schema
class WorkoutPlan(BaseModel):
    exercise: str
    sets: int

class WorkoutResponse(BaseModel):
    message: str
    plan: list[WorkoutPlan]
