from sqlalchemy import MetaData
from models import Base
from database import engine

Base.metadata.drop_all(bind=engine)  # DANGER: Drops all tables
Base.metadata.create_all(bind=engine)
print("Tables dropped and re-created.")
