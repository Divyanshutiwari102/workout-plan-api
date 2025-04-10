from sqlalchemy.orm import Session
from models import User

def create_user(db: Session, name: str, age: int, goal: str):
    db_user = User(name=name, age=age, goal=goal)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def update_user_goal(db: Session, user_id: int, new_goal: str):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.goal = new_goal
        db.commit()
        db.refresh(db_user)
    return db_user
