import sqlite3

# Connect to your new SQLite database
conn = sqlite3.connect('personalworkout.db')
c = conn.cursor()

# Drop the users table if it exists
c.execute("DROP TABLE IF EXISTS users")

# Recreate the users table with the new schema including 'feedback'
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        fitness_level TEXT,
        goal TEXT,
        plan TEXT,
        feedback TEXT
    )
''')

# Optional: Insert initial data with feedback
c.execute('''
    INSERT INTO users (name, age, gender, fitness_level, goal, plan, feedback) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', ('John Doe', 30, 'Male', 'Intermediate', 'Cardio', 'Running - 30 mins', 'Great workout'))

# Commit and close
conn.commit()
conn.close()

print("Database 'personalworkout.db' created with 'feedback' column!")
