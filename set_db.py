import sqlite3

conn = sqlite3.connect("fraudx.db")
cursor = conn.cursor()

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# PREDICTIONS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    time REAL,
    prediction_result TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully!")