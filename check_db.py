from database import SessionLocal
from models import User

# Check the first user in the database
def check_user_in_db():
    db = SessionLocal()
    user = db.query(User).first()
    if user:
        print(f"User found: {user.name}, Username: {user.username}")
    else:
        print("No users found.")
    db.close()

check_user_in_db()
