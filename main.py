from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
from typing import Optional
from passlib.context import CryptContext
from fpdf import FPDF
import sqlite3
from contextlib import closing
import tempfile
import os
import json
from pathlib import Path

app = FastAPI(title="Personalized Workout Plan Generator")

# ------------------ CORS and Static Setup ------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production: change this to allowed domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path("static").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ------------------ Password Context ------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ------------------ Database Setup ------------------
def get_db_connection():
    conn = sqlite3.connect("workout_plans.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
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
                health_constraints TEXT,
                password TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workout_plans (
                user_id INTEGER PRIMARY KEY,
                plan TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()

create_tables()

# ------------------ Models ------------------
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
    password: str

    @field_validator("age")
    def validate_age(cls, v):
        if v <= 0:
            raise ValueError("Age must be positive")
        return v

    @field_validator("workout_duration")
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError("Workout duration must be positive")
        return v

    @field_validator("goal")
    def validate_goal(cls, v):
        allowed = ["Muscle Gain", "Weight Loss", "Flexibility", "General Fitness"]
        if v not in allowed:
            raise ValueError(f"Goal must be one of {allowed}")
        return v

class LoginRequest(BaseModel):
    name: str
    password: str

# ------------------ Token Authentication ------------------
# Basic mock token validation
def get_current_user(x_token: str = Header(...)):
    if not x_token.startswith("token_"):
        raise HTTPException(status_code=403, detail="Not authenticated")
    return {"username": x_token[6:]}

# ------------------ Logic for Workout Plan ------------------
def generate_workout_plan(goal: str):
    plans = {
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
        ]
    }
    return plans.get(goal, [])

# ------------------ Endpoints ------------------

@app.post("/store-user/")
def store_user(user: UserCreate):
    try:
        hashed_pw = pwd_context.hash(user.password)
        plan = generate_workout_plan(user.goal)
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, age, gender, weight, height, fitness_level, goal, equipment, workout_duration, health_constraints, password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.name, user.age, user.gender, user.weight, user.height,
                user.fitness_level, user.goal, user.equipment,
                user.workout_duration, user.health_constraints, hashed_pw
            ))
            user_id = cursor.lastrowid
            cursor.execute('INSERT INTO workout_plans (user_id, plan) VALUES (?, ?)', (user_id, json.dumps(plan)))
            conn.commit()
            return {"message": "✅ User registered & workout plan saved", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/login/")
def login_user(login_req: LoginRequest):
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE name = ?", (login_req.name,))
            row = cursor.fetchone()
            if not row or not pwd_context.verify(login_req.password, row["password"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            token = f"token_{login_req.name}"
            return {"message": "✅ Login successful", "token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@app.get("/workout/{user_id}")
def get_workout(user_id: int, current_user: dict = Depends(get_current_user)):
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT plan FROM workout_plans WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Workout plan not found")
            return {"message": f"📋 Workout plan for user {user_id}", "plan": json.loads(row["plan"])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/profile/{user_id}")
def get_profile(user_id: int, current_user: dict = Depends(get_current_user)):
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="User not found")
            user_data = dict(row)
            user_data.pop("password", None)
            return {"profile": user_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ------------------ PDF Generation ------------------

def create_workout_pdf(plan, user_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Workout Plan for {user_name}", ln=True, align="C")
    pdf.ln(10)
    for idx, exercise in enumerate(plan, 1):
        text = f"{idx}. {exercise['exercise']} - {exercise['sets']} sets"
        pdf.cell(200, 10, txt=text, ln=True)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name

@app.get("/download/{user_id}")
def download_workout_plan(user_id: int, current_user: dict = Depends(get_current_user)):
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT u.name, wp.plan FROM users u JOIN workout_plans wp ON u.id = wp.user_id WHERE u.id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="User or workout plan not found")
            plan = json.loads(row["plan"])
            file_path = create_workout_pdf(plan, row["name"])
            safe_name = row["name"].replace(" ", "_")
            return FileResponse(file_path, media_type='application/pdf', filename=f"{safe_name}_workout_plan.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

@app.get("/")
def home():
    file_path = "static/index.html"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"message": "Welcome to the Workout Plan Generator API 🎯"}

# Optional: Admin route to get all users (disable in production)
@app.get("/users/")
def get_all_users():
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, goal FROM users")
        users = [dict(row) for row in cursor.fetchall()]
        return {"users": users}

# ------------------ Dev Startup ------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
