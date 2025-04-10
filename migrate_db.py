import sqlite3

# Connect to your new SQLite database (this will create a new file if it doesn't exist)
conn = sqlite3.connect('personalworkout.db')  # Use the new database name here
c = conn.cursor()

# Drop the users table if it exists
c.execute("DROP TABLE IF EXISTS users")

# Recreate the users table with the correct schema
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

# Insert some initial data (optional)
c.execute("INSERT INTO users (name, age, gender, fitness_level, goal, plan) VALUES (?, ?, ?, ?, ?, ?)", 
          ('John Doe', 30, 'Male', 'Intermediate', 'Cardio', 'Running - 30 mins'))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("New database 'personalworkout.db' created with 'plan' column!")
