import sqlite3

# Connect to your SQLite database
conn = sqlite3.connect('workout_plan.db')
c = conn.cursor()

# Check if the 'users' table exists, and create it if it doesn't
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

# Add the 'plan' column if it doesn't exist
try:
    c.execute('ALTER TABLE users ADD COLUMN plan TEXT')
except sqlite3.OperationalError:
    print("Column 'plan' already exists, skipping column creation.")

# Commit the changes
conn.commit()

# Close the connection
conn.close()

print("Database schema updated successfully!")
