import streamlit as st
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from passlib.hash import bcrypt
from fpdf import FPDF
# Make sure to import Base and engine
from database import Base, engine

# Automatically create all tables (only if they don't exist)
Base.metadata.create_all(bind=engine)

import base64
import os

# Password hashing
def hash_password(password):
    return bcrypt.hash(password)

def verify_password(password, hashed):
    return bcrypt.verify(password, hashed)

# DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Save user
def save_user_to_db(name, age, gender, fitness_level, goal, plan, username, password):
    db = SessionLocal()
    hashed_pw = hash_password(password)
    user = User(
        name=name,
        age=age,
        gender=gender,
        fitness_level=fitness_level,
        goal=goal,
        plan=plan,
        username=username,
        password_hash=hashed_pw
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Workout plan generator
def get_workout_plan(goal, fitness_level):
    plans = {
        'weight loss': {
            'beginner': ['🚶‍♂️ Walking - 30 mins', '🧘 Yoga - 20 mins', '🚴 Cycling - 15 mins'],
            'intermediate': ['🏃 Jogging - 40 mins', '💪 Bodyweight Circuit - 30 mins', '🚴 Cycling - 30 mins'],
            'advanced': ['🏋️ HIIT - 45 mins', '🏃‍♂️ Running - 60 mins', '🧘 Yoga - 30 mins']
        },
        'muscle gain': {
            'beginner': ['💪 Resistance Bands - 20 mins', '🏋️ Dumbbell Basics - 15 mins', '🧘 Stretching - 10 mins'],
            'intermediate': ['🏋️ Compound Lifts - 40 mins', '💪 Supersets - 30 mins', '🧘 Cooldown Stretch - 15 mins'],
            'advanced': ['🏋️ Heavy Lifting - 60 mins', '💥 Split Routines - 45 mins', '🧘 Active Recovery - 20 mins']
        }
    }
    return plans[goal][fitness_level]

# PDF generation
def generate_pdf(user, plan):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Personalized Workout Plan", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Name: {user.name}", ln=True)
    pdf.cell(200, 10, txt=f"Age: {user.age}", ln=True)
    pdf.cell(200, 10, txt=f"Goal: {user.goal}", ln=True)
    pdf.cell(200, 10, txt=f"Fitness Level: {user.fitness_level}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt="Workout Plan:", ln=True)
    for exercise in plan:
        pdf.cell(200, 10, txt=f"- {exercise}", ln=True)

    file_path = f"/tmp/{user.username}_plan.pdf"
    pdf.output(file_path)
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    return base64_pdf

# Session defaults
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# Login/Register UI
def login_register():
    st.title("🏋️ Personalized Workout App - Login/Register")
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            db = next(get_db())
            user = db.query(User).filter(User.username == username).first()
            if user and verify_password(password, user.password_hash):
                st.success(f"Welcome, {user.name}!")
                st.session_state.logged_in = True
                st.session_state.user = user
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")

    with tab2:
        st.subheader("Register")
        name = st.text_input("Full Name")
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        age = st.number_input("Age", min_value=10, max_value=100)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        fitness_level = st.selectbox("Fitness Level", ["beginner", "intermediate", "advanced"])
        goal = st.selectbox("Goal", ["weight loss", "muscle gain"])

        if st.button("Register"):
            db = next(get_db())
            if db.query(User).filter(User.username == new_username).first():
                st.error("Username already taken.")
            else:
                plan = ""
                save_user_to_db(name, age, gender, fitness_level, goal, plan, new_username, new_password)
                st.success("Registration successful! Please log in.")

# Main App
st.title("🏋️ Personalized Workout Plan Generator")

if not st.session_state.logged_in:
    login_register()
else:
    user = st.session_state.user
    with st.sidebar:
        st.header("👤 Update Your Info")
        age = st.number_input("Age", min_value=10, max_value=100, value=user.age)
        gender = st.radio("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(user.gender))
        fitness_level = st.selectbox("Fitness Level", ["beginner", "intermediate", "advanced"], index=["beginner", "intermediate", "advanced"].index(user.fitness_level))
        goal = st.selectbox("Goal", ["weight loss", "muscle gain"], index=["weight loss", "muscle gain"].index(user.goal))
        submit = st.button("Generate Plan ✅")

    if submit:
        plan = get_workout_plan(goal, fitness_level)
        st.subheader(f"📋 Workout Plan for {user.name}")
        st.markdown("### Here's your personalized routine:")
        for exercise in plan:
            st.success(exercise)

        # Update DB
        db = next(get_db())
        user.age = age
        user.gender = gender
        user.fitness_level = fitness_level
        user.goal = goal
        user.plan = ', '.join(plan)
        db.commit()
        st.success("Your workout plan has been saved!")

        # Download PDF
        base64_pdf = generate_pdf(user, plan)
        href = f'<a href="data:application/pdf;base64,{base64_pdf}" download="{user.username}_plan.pdf">📥 Download Workout Plan (PDF)</a>'
        st.markdown(href, unsafe_allow_html=True)

    # Sidebar options
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.experimental_rerun()

    if st.sidebar.button("📋 Show All Users"):
        db = next(get_db())
        users = db.query(User).all()
        st.subheader("🗃️ Stored Workout Plans")
        for u in users:
            st.markdown(f"**👤 {u.name}** | Age: {u.age} | Level: {u.fitness_level} | Goal: {u.goal}")
            st.success(f"Plan: {u.plan}")
        # Generate and offer PDF download
        def generate_pdf(plan, username):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=14)
            pdf.cell(200, 10, txt=f"{username}'s Workout Plan", ln=True, align='C')
            pdf.ln(10)
            for exercise in plan:
                pdf.cell(200, 10, txt=exercise, ln=True)
            pdf_file = f"{username}_plan.pdf"
            pdf.output(pdf_file)
            return pdf_file

        def download_button(file_path):
            with open(file_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            href = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="{file_path}">📥 Download Workout Plan (PDF)</a>'
            st.markdown(href, unsafe_allow_html=True)

        # Call the functions
        pdf_file = generate_pdf(plan, user.username)
        download_button(pdf_file)
