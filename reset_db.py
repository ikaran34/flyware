import sqlite3
import os
from datetime import datetime, timedelta

DB_FILE = 'flyware1.db'

if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create tables (same as in app.py)
cursor.execute('''CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

cursor.execute('''CREATE TABLE flights (
    flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_number TEXT NOT NULL,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    status TEXT NOT NULL,
    airline TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

cursor.execute('''CREATE TABLE alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    flight_id INTEGER NOT NULL,
    alert_type TEXT NOT NULL,
    message TEXT,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    notification_method TEXT DEFAULT 'email',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (flight_id) REFERENCES flights (flight_id)
)''')

cursor.execute('''CREATE TABLE user_settings (
    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    receive_email BOOLEAN DEFAULT 1,
    receive_sms BOOLEAN DEFAULT 0,
    phone_number TEXT,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
)''')

# Add sample flights
sample_flights = [
    ("BA212", "New York (JFK)", "London (LHR)", 
     (datetime.now() + timedelta(hours=2)).isoformat(),
     (datetime.now() + timedelta(hours=8)).isoformat(),
     "On Time", "British Airways"),
    ("AA102", "Los Angeles (LAX)", "Chicago (ORD)", 
     (datetime.now() + timedelta(hours=1)).isoformat(),
     (datetime.now() + timedelta(hours=4)).isoformat(),
     "On Time", "American Airlines"),
    ("DL143", "Atlanta (ATL)", "Miami (MIA)", 
     datetime.now().isoformat(),
     (datetime.now() + timedelta(hours=2)).isoformat(),
     "Delayed", "Delta Airlines")
]

for flight in sample_flights:
    cursor.execute('''
        INSERT INTO flights (flight_number, origin, destination, 
                            departure_time, arrival_time, status, airline)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', flight)

# Add test user
cursor.execute('''
    INSERT INTO users (username, password, email)
    VALUES (?, ?, ?)
''', (
    'testuser',
    'pbkdf2:sha256:260000$O87nanbS$...',  # Hash for 'password'
    'test@example.com'
))

user_id = cursor.lastrowid
cursor.execute('INSERT INTO user_settings (user_id) VALUES (?)', (user_id,))

conn.commit()
conn.close()

print("Database initialized successfully with sample data.")