# client/data_access.py

import requests
import json
import re

# --- CONFIGURATION (UPDATE THESE) ---
# Replace with your actual Django username and password
USERNAME = 'noamn' 
PASSWORD = 'admin' 
LOGIN_URL = 'http://127.0.0.1:8000/accounts/login/' 

# Local Django server URLs
BASE_URL = "http://127.0.0.1:8000/api/items/"
SENSOR_BASE_URL = "http://127.0.0.1:8000/api/"

# ------------------------------------------
# API CLIENT CLASS
# ------------------------------------------

class DjangoAPIClient:
    """
    Manages the session and authentication for all API interactions.
    """
    def __init__(self, username, password, login_url):
        # Create a session object to maintain cookies (login state)
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.login_url = login_url
        self.is_authenticated = False
        self.authenticate()



    def authenticate(self):
        """
        Performs the login sequence (GET for CSRF, then POST with credentials) 
        to establish an authenticated session.
        """
        # Initialize csrf_token_match to None to prevent NameError 
        # if an exception occurs before assignment.
        csrf_token_match = None
        
        # 1. First GET request to get the login page and the CSRF token
        print(f"Attempting GET on: {self.login_url}")
        try:
            login_page_response = self.session.get(self.login_url, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to server: {e}")
            return False

        # Extract the CSRF token from the login page HTML
        # This robust regex handles both single (' ) and double (" ) quotes 
        # around attribute values, fixing the previous issue.
        csrf_token_match = re.search(r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)["\']', 
                                     login_page_response.text)
        
        if not csrf_token_match:
            print("Error: Could not find CSRF token on login page. Check if LOGIN_URL is correct or if the page requires a different URL.")
            return False
            
        csrf_token = csrf_token_match.group(1)
        
        # 2. Data payload for the POST request
        login_data = {
            'username': self.username,
            'password': self.password,
            'csrfmiddlewaretoken': csrf_token,
            'next': '/'
        }
        
        # 3. Second POST request to log in
        print("Attempting POST login...")
        login_post_response = self.session.post(
            self.login_url, 
            data=login_data, 
            headers={'Referer': self.login_url},
            allow_redirects=False # Check for 302 redirect status explicitly
        )

        # Check for successful login (Django returns 302 Found on success)
        if login_post_response.status_code == 302 and login_post_response.headers.get('Location', '') in ('/', self.login_url):
            print("Login successful! Session established.")
            self.is_authenticated = True
            return True
        else:
            print(f"Login failed! Status: {login_post_response.status_code}. Check your credentials.")
            self.is_authenticated = False
            return False

    # ------------------------------------------
    # SENSOR FUNCTIONS
    # (Adapted to use self.session)
    # ------------------------------------------

    def get_sensors(self, item_id):
        """
        Fetch all sensors belonging to a given item using the authenticated session.
        """
        url = f"{SENSOR_BASE_URL}items/{item_id}/sensors/"
        r = self.session.get(url)
        
        if r.status_code == 200:
            try:
                return r.json()
            except json.JSONDecodeError:
                print("Error parsing sensors:", r.text)
                return []
        else:
            print("Error fetching sensors:", r.status_code, r.text)
            return []


    def create_sensor(self, item_id, plant_name, pump_thr=50, humidity=0, temp=0, light=0):
        """
        Create a new sensor for a specific item using the authenticated session.
        """
        url = f"{SENSOR_BASE_URL}items/{item_id}/sensors/create/"
        payload = {"plant_name": plant_name, "pump_thr": pump_thr,
                    "humidity": humidity, "temp": temp, "light": light}
        r = self.session.post(url, json=payload)
        try:
            print("Sensor created:" if r.status_code == 201 else "Error:", r.json())
        except json.JSONDecodeError:
            print("Error:", r.status_code, r.text)


    def update_sensor(self, sensor_id, **kwargs):
        """
        Update fields of an existing sensor by ID using the authenticated session.
        """
        url = f"{SENSOR_BASE_URL}sensors/{sensor_id}/update/"
        r = self.session.put(url, json=kwargs)
        try:
            print("Sensor updated:" if r.status_code == 200 else "Error:", r.json())
        except json.JSONDecodeError:
            print("Error:", r.status_code, r.text)


    def delete_sensor(self, sensor_id):
        """
        Delete a sensor by ID using the authenticated session.
        """
        url = f"{SENSOR_BASE_URL}sensors/{sensor_id}/delete/"
        r = self.session.delete(url)
        try:
            print("Sensor deleted:" if r.status_code == 204 else "Error:", r.json())
        except json.JSONDecodeError:
            print("Error:", r.status_code, r.text)

    # ------------------------------------------
    # ITEM FUNCTIONS
    # (Adapted to use self.session)
    # ------------------------------------------

    def get_items(self):
        """
        Fetch all items (from /api/items/) using the authenticated session.
        """
        response = self.session.get(BASE_URL)
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                print("Could not parse JSON:", response.text)
                return []
        else:
            print("Error fetching items:", response.status_code, response.text)
            return []


    def create_item(self, name, latitude, longitude):
        """
        Create a new item using the authenticated session.
        """
        payload = {"name": name, "latitude": latitude, "longitude": longitude}
        response = self.session.post(BASE_URL + "create/", json=payload)
        try:
            print("Item created:" if response.status_code == 201 else "Error:", response.json())
        except json.JSONDecodeError:
            print("Error creating item:", response.status_code, response.text)


    def update_item(self, item_id, name=None, latitude=None, longitude=None):
        """
        Update an existing item by ID using the authenticated session.
        """
        payload = {}
        if name:
            payload["name"] = name
        if latitude:
            payload["latitude"] = latitude
        if longitude:
            payload["longitude"] = longitude

        url = f"{BASE_URL}{item_id}/update/"
        response = self.session.put(url, json=payload)
        try:
            print("Item updated:" if response.status_code == 200 else "Error:", response.json())
        except json.JSONDecodeError:
            print("Error updating item:", response.status_code, response.text)


    def delete_item(self, item_id):
        """
        Delete an item by ID using the authenticated session.
        """
        url = f"{BASE_URL}{item_id}/delete/"
        response = self.session.delete(url)
        try:
            # Check for 204 No Content for successful deletion
            print("Item deleted:" if response.status_code == 204 else "Error:", response.json() if response.content else response.status_code)
        except json.JSONDecodeError:
            # If 204 is returned, there might be no content to decode
            if response.status_code == 204:
                print("Item deleted: 204 No Content")
            else:
                print("Error deleting item:", response.status_code, response.text)