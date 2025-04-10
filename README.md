Personalized Workout Plan Generator
Project Overview
This project is a web-based application that generates personalized workout plans based on user inputs, including fitness goals, preferences, and profile data. The app is built using FastAPI and PostgreSQL, offering an API that recommends exercises for users based on their fitness levels and goals.

Features
User Profile Input: Users can provide their fitness profile (e.g., age, weight, fitness goals).

Goal-based Workout Recommendation: Workout plans are tailored based on user goals (e.g., weight loss, strength training).

Database Integration: User data and workout plans are stored and retrieved from a PostgreSQL database.

Easy Deployment: The application is ready for deployment on Render.

Tech Stack
Backend: FastAPI

Database: PostgreSQL

Deployment: Render

Other Libraries:

SQLAlchemy

Pydantic

Uvicorn (ASGI server)

Alembic (for database migrations)

Installation
1. Clone the repository:
bash

git clone https://github.com/Divyanshutiwari102/workout-plan-api.git
cd workout-plan-api
2. Set up a virtual environment:
bash

python3 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
3. Install dependencies:
bash

pip install -r requirements.txt
4. Set up your environment variables:
Database URL: Add your PostgreSQL database URL in the .env file.

SECRET_KEY: Set a secret key for FastAPI.

5. Run the app locally:
bash

uvicorn main:app --reload
Your app will be available at http://127.0.0.1:8000.

Deployment on Render
To deploy the app on Render, follow these steps:

Create an Account on Render: If you don't already have a Render account, sign up at Render.

Create a New Web Service:

Connect your GitHub account and choose the repository (workout-plan-api).

Select the branch you want to deploy (e.g., main).

Choose the Python environment and set the build command as pip install -r requirements.txt.

Set the start command as uvicorn main:app --host 0.0.0.0 --port 8000.

Configure Environment Variables: Add necessary environment variables such as:

DATABASE_URL: Your PostgreSQL database URL.

SECRET_KEY: A secret key for the FastAPI application.

Deploy: Click "Create Web Service" and Render will automatically deploy the application. After deployment, you'll receive a public URL to access the app online.

Endpoints
1. GET /workout
Returns a workout plan based on the user's profile and goals.

2. POST /user
Accepts a user profile (e.g., age, fitness goals, weight) and stores it in the database.

Directory Structure
bash

.
├── app/
│   ├── crud.py            # CRUD operations
│   ├── database.py        # Database configuration and models
│   ├── main.py            # FastAPI app and routes
│   ├── models.py          # Database models
│   ├── schemas.py         # Pydantic schemas for validation
│   └── tasks.py           # Background tasks (e.g., workout plan generation)
├── .gitignore             # Git ignore rules (e.g., for .venv)
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
License
This project is licensed under the MIT License - see the LICENSE file for details
