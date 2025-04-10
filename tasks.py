import requests
from invoke import task

BASE_URL = "http://127.0.0.1:8000"

# Task to test POST /store-user/
@task
def test_post_user(c):
    data = {
        "name": "John Doe",
        "age": 30,
        "gender": "Male",
        "weight": 75.5,
        "height": 175,
        "fitness_level": "Beginner",
        "goal": "Weight Loss",
        "equipment": "None",
        "workout_duration": 30,
        "health_constraints": "None"
    }
    response = requests.post(f"{BASE_URL}/store-user/", json=data)
    print("POST /store-user/ response:")
    print(response.json())
# Task to test GET /workout/{user_id}
@task
def test_get_workout(c):
    user_id = 1  # Assuming you just added this user with user_id 1
    response = requests.get(f"{BASE_URL}/workout/{user_id}")
    print(f"GET /workout/{user_id} response:")
    print(response.json())
# Task to test PUT /update-user/{user_id}
@task
def test_put_user(c):
    user_id = 1  # User ID to update
    data = {
        "name": "John Doe Updated",
        "age": 31,
        "gender": "Male",
        "weight": 76.5,
        "height": 175,
        "fitness_level": "Intermediate",
        "goal": "Muscle Gain",
        "equipment": "Dumbbells",
        "workout_duration": 45,
        "health_constraints": "None"
    }
    response = requests.put(f"{BASE_URL}/update-user/{user_id}", json=data)
    print(f"PUT /update-user/{user_id} response:")
    print(response.json())
