# app.py
from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB = 'flyware.db'

# --- DB Utilities ---
def get_db():
    return sqlite3.connect(DB)

def init_db():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS flights (
            flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_number TEXT,
            origin TEXT,
            destination TEXT,
            departure_time TEXT,
            arrival_time TEXT,
            status TEXT
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS alerts (
            alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            flight_id INTEGER,
            alert_type TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        email = request.form['email']

        with get_db() as db:
            db.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                       (username, password, email))
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    with get_db() as db:
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
    return render_template('login.html', error='Invalid credentials')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    with get_db() as db:
        flights = db.execute('SELECT * FROM flights').fetchall()
    return render_template('dashboard.html', flights=flights)

@app.route('/alert', methods=['POST'])
def create_alert():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    flight_id = request.form['flight_id']
    alert_type = request.form['alert_type']
    user_id = session['user_id']

    with get_db() as db:
        db.execute('INSERT INTO alerts (user_id, flight_id, alert_type) VALUES (?, ?, ?)',
                   (user_id, flight_id, alert_type))
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
