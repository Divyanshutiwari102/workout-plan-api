from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from schemas import UserCreate, WorkoutResponse, WorkoutPlan

app = FastAPI()

# Connect to SQLite Database
conn = sqlite3.connect("workout.db", check_same_thread=False)
cursor = conn.cursor()

# Create Tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        weight REAL,
        height REAL,
        fitness_level TEXT,
        goal TEXT,
        equipment TEXT,
        workout_duration INTEGER,
        health_constraints TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        exercise TEXT,
        sets INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')

conn.commit()

# Home route
@app.get("/")
def home():
    return {"message": "🏋️‍♂️ Workout Plan API is running!"}

# Store user input data
@app.post("/store-user/")
def store_user(user: UserCreate):
    try:
        cursor.execute('''
            INSERT INTO users (name, age, gender, weight, height, fitness_level, goal, equipment, workout_duration, health_constraints)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user.name, user.age, user.gender, user.weight, user.height,
            user.fitness_level, user.goal, user.equipment,
            user.workout_duration, user.health_constraints
        ))
        conn.commit()
        user_id = cursor.lastrowid
        return {"message": "✅ User data stored successfully", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Sample Exercise DB
exercise_db = {
    "weight_loss": ["Jumping Jacks", "Burpees", "Mountain Climbers", "High Knees"],
    "muscle_gain": ["Push-ups", "Pull-ups", "Squats", "Lunges"],
    "flexibility": ["Yoga", "Stretching", "Pilates"],
    "general_fitness": ["Walking", "Jogging", "Bodyweight Circuit"]
}

# Workout request body
class WorkoutRequest(BaseModel):
    user_id: int

# Generate workout plan for an existing user
@app.post("/workout/", response_model=WorkoutResponse)
def generate_workout(data: WorkoutRequest):
    try:
        # Check if user exists
        cursor.execute("SELECT name, workout_duration, goal FROM users WHERE id = ?", (data.user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_name, duration, goal = user
        goal_key = goal.lower().replace(" ", "_")

        # Use sample DB or default
        base_plan = exercise_db.get(goal_key, exercise_db["general_fitness"])
        sets = max(1, duration // 10)
        workout_plan = [{"exercise": ex, "sets": sets} for ex in base_plan]

        # Save to workouts table
        for ex in workout_plan:
            cursor.execute('''
                INSERT INTO workouts (user_id, exercise, sets)
                VALUES (?, ?, ?)
            ''', (data.user_id, ex["exercise"], ex["sets"]))
        conn.commit()

        return {
            "message": f"💪 Workout plan for {user_name} ({goal})",
            "plan": workout_plan
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get workout by user ID
@app.get("/workout/{user_id}", response_model=WorkoutResponse)
def get_user_workout(user_id: int):
    try:
        cursor.execute("SELECT name, goal FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_name, goal = user

        cursor.execute("SELECT exercise, sets FROM workouts WHERE user_id = ?", (user_id,))
        workout_rows = cursor.fetchall()
        if not workout_rows:
            return {"message": f"No workout found for user {user_name}", "plan": []}

        workout_plan = [{"exercise": row[0], "sets": row[1]} for row in workout_rows]

        return {
            "message": f"🏋️ Workout plan for {user_name} ({goal})",
            "plan": workout_plan
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
