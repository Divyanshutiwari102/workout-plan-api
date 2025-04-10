from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional
import sqlite3
from contextlib import closing
from fastapi.responses import FileResponse
import os

# FastAPI instance
app = FastAPI()

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('workout_plans.db')
    conn.row_factory = sqlite3.Row  # To access columns by name
    return conn

# Create users table if not already present (it can be run once to set up the database)
def create_table():
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
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
                            health_constraints TEXT)''')
        conn.commit()

create_table()  # Run this once during app startup to create the table if it doesn't exist

# User input schema with validation
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

    # Custom validation for fields (updated for Pydantic V2)
    @field_validator('age')
    def validate_age(cls, value):
        if value <= 0:
            raise ValueError('Age must be a positive integer')
        return value

    @field_validator('workout_duration')
    def validate_duration(cls, value):
        if value <= 0:
            raise ValueError('Workout duration must be a positive integer')
        return value

    @field_validator('goal')
    def validate_goal(cls, value):
        allowed_goals = ['Muscle Gain', 'Weight Loss', 'Flexibility', 'General Fitness']
        if value not in allowed_goals:
            raise ValueError(f'Goal must be one of {allowed_goals}')
        return value

# Function to generate a workout plan based on the user's goal
def generate_workout_plan(goal: str):
    # Define hardcoded workout plans for each goal
    workout_plans = {
        "Muscle Gain": [
            {"exercise": "Push-ups", "sets": 4},
            {"exercise": "Pull-ups", "sets": 4},
            {"exercise": "Squats", "sets": 4},
            {"exercise": "Lunges", "sets": 4},
        ],
        "Weight Loss": [
            {"exercise": "Running", "sets": 3},
            {"exercise": "Jump Rope", "sets": 3},
            {"exercise": "Cycling", "sets": 3},
        ],
        "Flexibility": [
            {"exercise": "Yoga Poses", "sets": 3},
            {"exercise": "Stretching", "sets": 3},
        ],
        "General Fitness": [
            {"exercise": "Push-ups", "sets": 3},
            {"exercise": "Squats", "sets": 3},
            {"exercise": "Running", "sets": 3},
        ],
    }
    
    # Return the workout plan for the specified goal
    return workout_plans.get(goal, [])

# Store user endpoint
@app.post("/store-user/")
def store_user(user: UserCreate):
    try:
        # Insert validated data into the database
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO users (name, age, gender, weight, height, fitness_level, goal, equipment, workout_duration, health_constraints)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                user.name, user.age, user.gender, user.weight, user.height, user.fitness_level, 
                user.goal, user.equipment, user.workout_duration, user.health_constraints
            ))
            conn.commit()
            user_id = cursor.lastrowid
            return {"message": "✅ User data stored successfully", "user_id": user_id}
    
    except ValueError as ve:
        # Handle validation errors
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Handle other unexpected errors
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Endpoint to get a workout plan based on user_id
@app.get("/workout/{user_id}")
def get_workout_plan(user_id: int):
    try:
        # Retrieve user data from the database
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT goal FROM users WHERE id = ?''', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get the user's goal from the database
            goal = user['goal']
            
            # Generate the workout plan based on the user's goal
            workout_plan = generate_workout_plan(goal)
            
            if not workout_plan:
                raise HTTPException(status_code=404, detail="No workout plan found for this goal")
            
            # Return the workout plan
            return {"message": f"Workout plan for {goal} goal", "plan": workout_plan}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Endpoint to fetch user details
@app.get("/user/{user_id}")
def get_user(user_id: int):
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT * FROM users WHERE id = ?''', (user_id,))
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return dict(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")

# Endpoint to update user profile by user_id
@app.put("/update-user/{user_id}")
def update_user(user_id: int, user: UserCreate):
    try:
        # Check if the user exists
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT * FROM users WHERE id = ?''', (user_id,))
            existing_user = cursor.fetchone()
            
            if not existing_user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Update user details
            cursor.execute('''UPDATE users SET 
                                name = ?, 
                                age = ?, 
                                gender = ?, 
                                weight = ?, 
                                height = ?, 
                                fitness_level = ?, 
                                goal = ?, 
                                equipment = ?, 
                                workout_duration = ?, 
                                health_constraints = ? 
                               WHERE id = ?''', (
                user.name, user.age, user.gender, user.weight, user.height, user.fitness_level,
                user.goal, user.equipment, user.workout_duration, user.health_constraints, user_id
            ))
            conn.commit()

            return {"message": "✅ User profile updated successfully"}
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

# Run the app with uvicorn if running as the main module
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))  # Get port from environment variable or default to 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
