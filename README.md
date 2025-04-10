# 🏋️ Personalized Workout Plan Generator

A FastAPI-based backend that recommends personalized workout routines based on user inputs like age, gender, fitness level, goals, and available equipment.

## 🚀 Features

- Store user profile and preferences
- AI-inspired rule-based workout recommendations
- Retrieve personalized plans
- SQLite database for lightweight local storage

## 📦 Tech Stack

- FastAPI (Python)
- SQLite (for local DB)
- Pydantic (validation)
- Uvicorn (server)

## 📂 Endpoints

### 1. Home
GET /

shell


### 2. Store User Info

POST /store-user/

shell


### 3. Generate Workout Plan

POST /workout/

pgsql


### 4. Get Workout by User ID

GET /workout/{user_id}

perl


## ▶️ Run Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
Visit http://localhost:8000/docs for Swagger UI.

📁 Folder Structure
css

.
├── main.py
├── schemas.py
├── requirements.txt
├── Procfile
├── README.md
