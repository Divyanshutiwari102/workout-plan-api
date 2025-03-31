from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Connect to SQLite Database
conn = sqlite3.connect("workout.db", check_same_thread=False)
cursor = conn.cursor()

# Create Users Table
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
conn.commit()

# Pydantic Model for JSON Request Body
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
    health_constraints: str | None = None  # Optional field

# Root Endpoint
@app.get("/")
def home():
    return {"message": "Workout Plan API is running!"}

# API to Store User Data
@app.post("/store-user/")
def store_user(user: User):
    try:
        cursor.execute('''
            INSERT INTO users (name, age, gender, weight, height, fitness_level, goal, equipment, workout_duration, health_constraints)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user.name, user.age, user.gender, user.weight, user.height, user.fitness_level, user.goal, user.equipment, user.workout_duration, user.health_constraints))
        conn.commit()
        return {"message": "User data stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API to Retrieve All Users
@app.get("/users/")
def get_users():
    try:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        if not users:
            return {"message": "No users found"}
        user_list = [
            {
                "id": user[0],
                "name": user[1],
                "age": user[2],
                "gender": user[3],
                "weight": user[4],
                "height": user[5],
                "fitness_level": user[6],
                "goal": user[7],
                "equipment": user[8],
                "workout_duration": user[9],
                "health_constraints": user[10]
            }
            for user in users
        ]
        return {"users": user_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
