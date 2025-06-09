# populate_flights.py
import sqlite3

flights = [
    ("BA212", "New York (JFK)", "London (LHR)", "2025-06-10 19:30", "2025-06-11 07:15", "On Time"),
    ("EK202", "Dubai (DXB)", "New York (JFK)", "2025-06-11 02:30", "2025-06-11 08:55", "Delayed"),
    ("AF083", "San Francisco (SFO)", "Paris (CDG)", "2025-06-10 15:45", "2025-06-11 10:20", "On Time"),
    ("LH401", "Frankfurt (FRA)", "New York (JFK)", "2025-06-10 13:00", "2025-06-10 16:30", "Cancelled"),
    ("SQ321", "London (LHR)", "Singapore (SIN)", "2025-06-09 22:05", "2025-06-10 18:00", "On Time"),
    ("CX888", "Hong Kong (HKG)", "Vancouver (YVR)", "2025-06-08 23:55", "2025-06-09 19:45", "Delayed"),
    ("DL404", "Atlanta (ATL)", "Los Angeles (LAX)", "2025-06-10 10:30", "2025-06-10 12:45", "On Time"),
    ("QF12", "Los Angeles (LAX)", "Sydney (SYD)", "2025-06-11 22:30", "2025-06-13 06:30", "On Time"),
    ("TK10", "Istanbul (IST)", "Chicago (ORD)", "2025-06-10 14:25", "2025-06-10 17:55", "Delayed"),
    ("NH7", "Tokyo (NRT)", "San Francisco (SFO)", "2025-06-12 17:00", "2025-06-12 09:00", "On Time"),
]

conn = sqlite3.connect('flyware1.db')
cursor = conn.cursor()

cursor.execute('DELETE FROM flights')  # Optional: clear old data

for flight in flights:
    cursor.execute('''
        INSERT INTO flights (flight_number, origin, destination, departure_time, arrival_time, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', flight)

conn.commit()
conn.close()
print("Realistic flight schedule added.")
