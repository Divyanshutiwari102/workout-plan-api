from sqlalchemy import MetaData
from models import Base
from database import engine

def recreate_tables():
    confirm = input("⚠️ This will DELETE all existing tables and data. Type 'yes' to continue: ")
    if confirm.lower() == 'yes':
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ Tables dropped and re-created.")
    else:
        print("❌ Operation cancelled.")

if __name__ == "__main__":
    recreate_tables()
