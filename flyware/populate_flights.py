import sqlite3

flights = [
    ("FW101", "New York", "London", "2025-06-10 08:30", "2025-06-10 20:45", "On Time"),
    ("FW102", "Paris", "Tokyo", "2025-06-11 12:00", "2025-06-12 04:15", "Delayed"),
    ("FW103", "Sydney", "Dubai", "2025-06-09 22:00", "2025-06-10 05:30", "On Time"),
    ("FW104", "Toronto", "Berlin", "2025-06-08 07:45", "2025-06-08 18:00", "Cancelled"),
    ("FW105", "Los Angeles", "Chicago", "2025-06-07 13:20", "2025-06-07 17:00", "On Time"),
]

conn = sqlite3.connect('flyware.db')
cursor = conn.cursor()

for flight in flights:
    cursor.execute('''
        INSERT INTO flights (flight_number, origin, destination, departure_time, arrival_time, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', flight)

conn.commit()
conn.close()

print("Sample flights added.")
