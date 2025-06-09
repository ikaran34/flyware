import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def get_live_flights():
    """Fetch live flight data from OpenSky Network API"""
    try:
        url = 'https://opensky-network.org/api/states/all'
        
        # Use environment variables for credentials
        auth = HTTPBasicAuth(
            os.getenv('OPENSKY_USERNAME', 'default_username'),
            os.getenv('OPENSKY_PASSWORD', 'default_password')
        )
        
        # Get flights within the last 2 hours
        now = datetime.utcnow()
        begin = int((now - timedelta(hours=2)).timestamp())
        end = int(now.timestamp())
        
        params = {
            'lamin': 20,  # Latitude minimum (southern boundary)
            'lamax': 50,  # Latitude maximum (northern boundary)
            'lomin': -130, # Longitude minimum (western boundary)
            'lomax': -60,  # Longitude maximum (eastern boundary)
            'begin': begin,
            'end': end
        }
        
        response = requests.get(url, auth=auth, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        if data.get('states'):
            print(f"OpenSky API returned {len(data['states'])} flights")
            return data['states']
        
        print("OpenSky API returned no flight data")
        return []
        
    except requests.exceptions.RequestException as e:
        print(f"OpenSky API error: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None