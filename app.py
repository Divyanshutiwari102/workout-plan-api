import streamlit as st
import sqlite3

# Function to create or connect to the database
def create_connection():
    conn = sqlite3.connect('personalworkout.db')  # Connect to the new database
    return conn

# Function to create the 'users' table if it doesn't exist
def create_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            fitness_level TEXT,
            goal TEXT,
            plan TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the table creation on app start
create_table()

# Workout plans database
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

# App title
st.title("🏋️ Personalized Workout Plan Generator")

# Sidebar inputs
with st.sidebar:
    st.header("👤 User Information")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=10, max_value=100)
    gender = st.radio("Gender", ["Male", "Female", "Other"])
    fitness_level = st.selectbox("Fitness Level", ["beginner", "intermediate", "advanced"])
    goal = st.selectbox("Goal", ["weight loss", "muscle gain"])
    submit = st.button("Generate Plan ✅")

# Output section
if submit:
    if name and age and fitness_level and goal:
        plan = plans[goal][fitness_level]
        st.subheader(f"📋 Workout Plan for {name}")
        st.markdown("### Here's your personalized routine:")
        for exercise in plan:
            st.success(exercise)

        # Save to database
        conn = create_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (name, age, gender, fitness_level, goal, plan) VALUES (?, ?, ?, ?, ?, ?)",
                  (name, age, gender, fitness_level, goal, ', '.join(plan)))
        conn.commit()
        conn.close()

    else:
        st.warning("Please fill out all fields.")
