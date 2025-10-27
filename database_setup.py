import sqlite3

# Connect to (or create) the database file
conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# Create the students table
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    enrollment_number TEXT NOT NULL UNIQUE
);
''')

# Create the attendance table
cursor.execute('''
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    timestamp TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students (id)
);
''')

print("Database and tables created successfully. ✔️")

conn.commit()
conn.close()