import streamlit as st
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import User
from passlib.hash import bcrypt
from fpdf import FPDF
import base64
import os
import re

# Create DB tables
Base.metadata.create_all(bind=engine)

# Password utilities
def hash_password(password):
    return bcrypt.hash(password)

def verify_password(password, hashed):
    return bcrypt.verify(password, hashed)

# DB session context
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Save user to database
def save_user_to_db(name, age, gender, fitness_level, goal, plan, username, password):
    with next(get_db()) as db:
        hashed_pw = hash_password(password)
        user = User(
            name=name.strip(),
            age=age,
            gender=gender,
            fitness_level=fitness_level,
            goal=goal,
            plan=plan,
            username=username.strip(),
            password_hash=hashed_pw
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

# Workout plan logic
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

# Remove emojis for PDF compatibility
def remove_emojis(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

# PDF generator
def generate_pdf(user, plan):
    pdf = FPDF()
    pdf.add_page()

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if os.path.exists(font_path):
        pdf.add_font('DejaVu', '', font_path, uni=True)
        pdf.set_font('DejaVu', '', 12)
    else:
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
        clean_text = remove_emojis(exercise)
        pdf.cell(200, 10, txt=f"- {clean_text}", ln=True)

    file_path = os.path.join("/tmp", f"{user.username}_plan.pdf")
    pdf.output(file_path)

    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    return base64_pdf

# Session state init
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
            with next(get_db()) as db:
                user = db.query(User).filter(User.username == username.strip()).first()
                if user and verify_password(password, user.password_hash):
                    st.success(f"Welcome, {user.name}!")
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
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
            with next(get_db()) as db:
                if db.query(User).filter(User.username == new_username.strip()).first():
                    st.error("Username already taken.")
                else:
                    save_user_to_db(name, age, gender, fitness_level, goal, "", new_username, new_password)
                    st.success("Registration successful! Please log in.")

# Main app
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
        with next(get_db()) as db:
            user.age = age
            user.gender = gender
            user.fitness_level = fitness_level
            user.goal = goal
            user.plan = ', '.join(plan)
            db.merge(user)
            db.commit()
            st.success("Your workout plan has been saved!")

        # PDF Download
        base64_pdf = generate_pdf(user, plan)
        href = f'<a href="data:application/pdf;base64,{base64_pdf}" download="{user.username}_plan.pdf">📥 Download Workout Plan (PDF)</a>'
        st.markdown(href, unsafe_allow_html=True)

    # Sidebar options
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    if st.sidebar.button("📋 Show All Users"):
        with next(get_db()) as db:
            users = db.query(User).all()
            st.subheader("🗃️ Stored Workout Plans")
            for u in users:
                st.markdown(f"**👤 {u.name}** | Age: {u.age} | Level: {u.fitness_level} | Goal: {u.goal}")
                st.success(f"Plan: {u.plan}")
