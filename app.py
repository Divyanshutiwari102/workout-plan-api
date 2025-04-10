import streamlit as st

# Workout generator function
def generate_workout_plan(goal):
    if goal == "Weight Loss":
        return ["Jumping jacks", "Burpees", "Mountain climbers"]
    elif goal == "Muscle Gain":
        return ["Deadlifts", "Bench press", "Squats"]
    elif goal == "Flexibility":
        return ["Yoga", "Stretching", "Pilates"]
    else:
        return ["Walking", "Cycling", "General Fitness"]

# UI
st.title("🏋️ Personalized Workout Plan Generator")

name = st.text_input("Enter your name:")
goal = st.selectbox("Select your fitness goal:", ["Weight Loss", "Muscle Gain", "Flexibility", "General Fitness"])

if st.button("Generate Workout Plan"):
    if name and goal:
        plan = generate_workout_plan(goal)
        st.success(f"Hey {name}! Here's your workout plan:")
        for exercise in plan:
            st.markdown(f"- {exercise}")
    else:
        st.error("Please fill in all fields.")
