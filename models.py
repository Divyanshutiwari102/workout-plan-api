from sqlalchemy import Column, Integer, String, Float
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    weight = Column(Float)
    height = Column(Float)
    fitness_level = Column(String)
    goal = Column(String)
    equipment = Column(String)
    workout_duration = Column(Integer)
    health_constraints = Column(String)

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    exercise = Column(String)
    sets = Column(Integer)
