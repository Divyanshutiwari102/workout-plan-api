from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3

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

# Pydantic Model
class User(BaseModel):
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

# Root Endpoint
@app.get("/")
def home():
    return {"message": "Workout Plan API is running!"}

# Store User Data
@app.post("/store-user/")
def store_user(user: User):
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
        return {"message": "User data stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get All Users
@app.get("/users/")
def get_users():
    try:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        if not users:
            return {"message": "No users found"}
        return {
            "users": [
                {
                    "id": u[0], "name": u[1], "age": u[2], "gender": u[3],
                    "weight": u[4], "height": u[5], "fitness_level": u[6],
                    "goal": u[7], "equipment": u[8], "workout_duration": u[9],
                    "health_constraints": u[10]
                } for u in users
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Sample Exercise Database
exercise_db = {
    "weight_loss": ["Jumping Jacks", "Burpees", "Mountain Climbers", "High Knees"],
    "muscle_gain": ["Push-ups", "Pull-ups", "Squats", "Lunges"],
    "flexibility": ["Yoga", "Stretching", "Pilates"],
    "general_fitness": ["Walking", "Jogging", "Bodyweight Circuit"]
}

# Generate Workout Plan and Store It
@app.post("/workout/")
def generate_workout(user: User):
    try:
        # Insert user
        cursor.execute('''
            INSERT INTO users (name, age, gender, weight, height, fitness_level, goal, equipment, workout_duration, health_constraints)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user.name, user.age, user.gender, user.weight, user.height,
            user.fitness_level, user.goal, user.equipment,
            user.workout_duration, user.health_constraints
        ))
        conn.commit()

        # Get user_id of the inserted user
        user_id = cursor.lastrowid

        # Generate workout
        goal = user.goal.lower().replace(" ", "_")
        fitness_level = user.fitness_level.lower()
        equipment = user.equipment.lower()
        duration = user.workout_duration

        base_plan = exercise_db.get(goal, exercise_db["general_fitness"])
        sets = max(1, duration // 10)
        workout_plan = [{"exercise": ex, "sets": sets} for ex in base_plan]

        # Store workout in DB
        for ex in workout_plan:
            cursor.execute('''
                INSERT INTO workouts (user_id, exercise, sets)
                VALUES (?, ?, ?)
            ''', (user_id, ex["exercise"], ex["sets"]))
        conn.commit()

        return {
            "message": f"Workout plan for {user.name} ({goal.title()})",
            "plan": workout_plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Retrieve Workout Plan by User ID
@app.get("/workout/{user_id}")
def get_user_workout(user_id: int):
    try:
        # Get user info
        cursor.execute("SELECT name, goal FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_name, goal = user

        # Get user's workout plan
        cursor.execute("SELECT exercise, sets FROM workouts WHERE user_id = ?", (user_id,))
        workout_rows = cursor.fetchall()

        if not workout_rows:
            return {"message": f"No workout found for user {user_name}"}

        workout_plan = [{"exercise": row[0], "sets": row[1]} for row in workout_rows]

        return {
            "message": f"Workout plan for {user_name} ({goal})",
            "plan": workout_plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
