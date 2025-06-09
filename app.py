from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Database configuration
DB = 'flyware1.db'

# OpenSky credentials
OPENSKY_USERNAME = 'eddy1'
OPENSKY_PASSWORD = 'Karan@1234'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        # Users table
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Flights table (updated for OpenSky data)
        db.execute('''CREATE TABLE IF NOT EXISTS flights (
            flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
            callsign TEXT,
            origin_country TEXT,
            longitude REAL,
            latitude REAL,
            altitude REAL,
            velocity REAL,
            vertical_rate REAL,
            on_ground BOOLEAN,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Alerts table
        db.execute('''CREATE TABLE IF NOT EXISTS alerts (
            alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            flight_id INTEGER NOT NULL,
            alert_type TEXT NOT NULL,
            message TEXT,
            start_time TEXT DEFAULT CURRENT_TIMESTAMP,
            end_time TEXT,
            status TEXT DEFAULT 'active',
            notification_method TEXT DEFAULT 'email',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (flight_id) REFERENCES flights (flight_id)
        )''')
        
        # Create indexes
        db.execute('CREATE INDEX IF NOT EXISTS idx_flights_coords ON flights(longitude, latitude)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id)')

def get_opensky_flights():
    """Fetch real-time flight data from OpenSky Network"""
    try:
        auth = HTTPBasicAuth(OPENSKY_USERNAME, OPENSKY_PASSWORD)
        url = "https://opensky-network.org/api/states/all"
        response = requests.get(url, auth=auth, timeout=10)
        data = response.json()
        
        if 'states' in data:
            return data['states']
        return []
    except Exception as e:
        print(f"Error fetching from OpenSky API: {str(e)}")
        return []

def update_flights_data():
    """Update flights database with OpenSky data"""
    opensky_flights = get_opensky_flights()
    if not opensky_flights:
        return False
    
    with get_db() as db:
        db.execute('DELETE FROM flights')
        
        for flight in opensky_flights[:200]:  # Limit to 200 flights
            try:
                db.execute('''
                    INSERT INTO flights (
                        callsign, origin_country, longitude, latitude,
                        altitude, velocity, vertical_rate, on_ground
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    flight[1].strip() if flight[1] else None,  # callsign
                    flight[2],                                # origin_country
                    flight[5],                                # longitude
                    flight[6],                                # latitude
                    flight[7],                                # altitude
                    flight[9],                                # velocity
                    flight[11],                               # vertical_rate
                    bool(flight[8])                           # on_ground
                ))
            except Exception as e:
                print(f"Error inserting flight: {str(e)}")
                continue
    
    return True

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        if not all([username, password, email]):
            flash('Please fill in all fields', 'error')
            return redirect(url_for('register'))
        
        try:
            hashed_password = generate_password_hash(password)
            with get_db() as db:
                db.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                          (username, hashed_password, email))
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists', 'error')
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    with get_db() as db:
        user = db.execute('SELECT user_id, username, password FROM users WHERE username = ?', 
                         (username,)).fetchone()
    
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    
    flash('Invalid username or password', 'error')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    try:
        update_flights_data()  # Refresh flight data on each dashboard load
        with get_db() as db:
            flights = db.execute('SELECT * FROM flights LIMIT 100').fetchall()
            
        return render_template('dashboard.html', flights=flights)
    except Exception as e:
        flash(f'Error loading flights: {str(e)}', 'error')
        return render_template('dashboard.html', flights=[])

@app.route('/alerts')
def alerts():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    try:
        with get_db() as db:
            alerts = db.execute('''
                SELECT a.*, f.callsign, f.origin_country 
                FROM alerts a
                JOIN flights f ON a.flight_id = f.flight_id
                WHERE a.user_id = ?
            ''', (session['user_id'],)).fetchall()
            
            flights = db.execute('SELECT flight_id, callsign FROM flights LIMIT 50').fetchall()
        
        return render_template('alerts.html', alerts=alerts, flights=flights)
    except Exception as e:
        flash(f'Error loading alerts: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/alert/create', methods=['POST'])
def create_alert():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    try:
        flight_id = request.form['flight_id']
        alert_type = request.form['alert_type']
        message = request.form.get('message', '')
        notification_method = request.form['notification_method']
        end_time = request.form.get('end_time', (datetime.now() + timedelta(hours=24)).isoformat())
        
        with get_db() as db:
            db.execute('''
                INSERT INTO alerts (
                    user_id, flight_id, alert_type, message, 
                    notification_method, end_time
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session['user_id'],
                flight_id,
                alert_type,
                message,
                notification_method,
                end_time
            ))
        
        flash('Alert created successfully!', 'success')
    except Exception as e:
        flash(f'Error creating alert: {str(e)}', 'error')
    
    return redirect(url_for('alerts'))

@app.route('/alert/<int:alert_id>/edit', methods=['POST'])
def edit_alert(alert_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    try:
        data = request.form
        with get_db() as db:
            db.execute('''
                UPDATE alerts SET
                    alert_type = ?,
                    message = ?,
                    notification_method = ?,
                    end_time = ?,
                    status = ?
                WHERE alert_id = ? AND user_id = ?
            ''', (
                data['alert_type'],
                data.get('message', ''),
                data['notification_method'],
                data.get('end_time', (datetime.now() + timedelta(hours=24)).isoformat()),
                data['status'],
                alert_id,
                session['user_id']
            ))
        
        flash('Alert updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating alert: {str(e)}', 'error')
    
    return redirect(url_for('alerts'))

@app.route('/alert/<int:alert_id>/delete', methods=['POST'])
def delete_alert(alert_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    try:
        with get_db() as db:
            db.execute('DELETE FROM alerts WHERE alert_id = ? AND user_id = ?', 
                      (alert_id, session['user_id']))
        
        flash('Alert deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting alert: {str(e)}', 'error')
    
    return redirect(url_for('alerts'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    with get_db() as db:
        user = db.execute('SELECT username, email FROM users WHERE user_id = ?', 
                         (session['user_id'],)).fetchone()
    
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/api/flights')
def api_flights():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        with get_db() as db:
            flights = db.execute('''
                SELECT flight_id, callsign, origin_country, 
                       longitude, latitude, altitude, velocity, 
                       vertical_rate, on_ground
                FROM flights
                LIMIT 100
            ''').fetchall()
            
            return jsonify([dict(flight) for flight in flights])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)