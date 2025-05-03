from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    fitness_level = Column(String)
    goal = Column(String)
    plan = Column(String)

    workout_plans = relationship("WorkoutPlan", back_populates="user")

class WorkoutPlan(Base):
    __tablename__ = 'workout_plans'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    day = Column(String)
    exercise = Column(String)
    sets = Column(String)
    reps = Column(String)

    user = relationship("User", back_populates="workout_plans")
