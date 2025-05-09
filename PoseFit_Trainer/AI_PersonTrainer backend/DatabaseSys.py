import json
import os
import re
from pathlib import Path
import EmailingSystem as email_sys
import time
from passlib.context import CryptContext

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Constants
USER_DB_FILE = 'user_data.json'

# Always use absolute path for user database
USER_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), USER_DB_FILE)

def validate_email(email):
    """Validate email format using regex pattern"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"[Database] Password verification error: {str(e)}")
        return False

def load_user_database():
    """Load user database from file, creating it if it doesn't exist"""
    try:
        db_path = USER_DB_PATH
        print(f"[Database] Using database file: {db_path}")
        
        # Create new database if it doesn't exist
        if not os.path.exists(db_path):
            print(f"[Database] Creating new user database file: {db_path}")
            data = {}
            with open(db_path, 'w') as f:
                json.dump(data, f, indent=4)
            return data
        
        # Try to load existing database
        print(f"[Database] Loading user database from: {db_path}")
        try:
            with open(db_path, 'r') as f:
                data = json.load(f)
                
            # Validate database structure
            if not isinstance(data, dict):
                print("[Database] Invalid database format, creating new database")
                data = {}
                
            # Create backup of old data
            backup_path = db_path + '.bak'
            with open(backup_path, 'w') as f:
                json.dump(data, f, indent=4)
                
            # Save validated/fixed data
            with open(db_path, 'w') as f:
                json.dump(data, f, indent=4)
                
            return data
            
        except json.JSONDecodeError:
            print("[Database] Database file is corrupted, creating new database")
            data = {}
            with open(db_path, 'w') as f:
                json.dump(data, f, indent=4)
            return data
            
    except Exception as e:
        print(f"[Database] Error accessing database: {e}")
        print("[Database] Creating new empty database")
        data = {}
        try:
            with open(db_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as write_error:
            print(f"[Database] Warning: Could not write database file: {write_error}")
        return data

def save_user_database(user_db):
    """Save user database to file"""
    if not isinstance(user_db, dict):
        print("[Database] Invalid database format")
        return False
        
    try:
        # Create a backup of the current database
        if os.path.exists(USER_DB_PATH):
            backup_file = USER_DB_PATH + '.bak'
            try:
                with open(USER_DB_PATH, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
                print(f"[Database] Created backup at: {backup_file}")
            except Exception as e:
                print(f"[Database] Warning: Could not create backup: {e}")
        
        # Save the new data
        with open(USER_DB_PATH, 'w') as f:
            json.dump(user_db, f, indent=4)
        print("[Database] Database saved successfully")
        return True
    except Exception as e:
        print(f"[Database] Error saving database: {e}")
        return False

def authenticate_user(email: str, password: str):
    """Authenticate a user by email and password"""
    print(f"[Database] Attempting to authenticate user: {email}")
    
    if not validate_email(email):
        print("[Database] Invalid email format")
        return None
    
    user_db = load_user_database()
    if not user_db:
        print("[Database] User database is empty")
        return None
    
    user = user_db.get(email)
    if not user:
        print(f"[Database] User not found: {email}")
        return None
    
    # Check for both old and new password field names
    stored_hash = user.get("hashed_password") or user.get("password")
    if not stored_hash:
        print("[Database] No password hash found")
        return None
    
    # Verify password
    if not verify_password(password, stored_hash):
        print("[Database] Invalid password")
        return None
    
    # If using old password field, migrate to new field name
    if "password" in user and "hashed_password" not in user:
        user["hashed_password"] = user["password"]
        del user["password"]
        save_user_database(user_db)
    
    print(f"[Database] User authenticated successfully: {email}")
    return user

def register_user_api(user_data):
    """Register a new user through the API"""
    try:
        print(f"[Database] Attempting to register user: {user_data['email']}")
        
        if not validate_email(user_data["email"]):
            print("[Database] Invalid email format")
            raise ValueError("Invalid email format")
        
        if not user_data.get("password"):
            print("[Database] Password is required")
            raise ValueError("Password is required")
            
        user_db = load_user_database()
        
        email = user_data["email"]
        if email in user_db:
            print("[Database] Email already registered")
            raise ValueError("Email already registered")
        
        # Hash the password
        try:
            hashed_password = get_password_hash(user_data["password"])
            print("[Database] Password hashed successfully")
        except Exception as e:
            print(f"[Database] Error hashing password: {str(e)}")
            raise Exception("Error processing password")
        
        # Create user data structure
        new_user = {
            "email": email,
            "hashed_password": hashed_password,  # Use new field name
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "age": user_data["age"],
            "gender": user_data["gender"],
            "weight": user_data["weight"],
            "height": user_data["height"],
            "verified": False,
            "verification_time": time.time()
        }
        
        # Save to database
        user_db[email] = new_user
        if not save_user_database(user_db):
            print("[Database] Failed to save user data")
            raise Exception("Failed to save user data")
        
        print(f"[Database] User registered successfully: {email}")
        
        # Return user data without sensitive information
        return {
            "email": email,
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "age": user_data["age"],
            "gender": user_data["gender"],
            "weight": user_data["weight"],
            "height": user_data["height"],
            "verified": False
        }
        
    except ValueError as e:
        print(f"[Database] Validation error: {str(e)}")
        raise
    except Exception as e:
        print(f"[Database] Error registering user: {str(e)}")
        raise

def save_workout_session(self, workout_data):
    """Save a new workout session to the database"""
    try:
        # Load existing workout sessions
        workouts_file = os.path.join(self.base_dir, 'saved_workouts', 'workout_sessions.json')
        
        if os.path.exists(workouts_file):
            with open(workouts_file, 'r') as f:
                workouts = json.load(f)
        else:
            workouts = []
        
        # Add new workout session
        workouts.append(workout_data)
        
        # Save updated workouts
        os.makedirs(os.path.dirname(workouts_file), exist_ok=True)
        with open(workouts_file, 'w') as f:
            json.dump(workouts, f, indent=4)
            
        return True
        
    except Exception as e:
        print(f"Error saving workout session: {str(e)}")
        return False

def update_workout_session(self, session_id, update_data):
    """Update an existing workout session"""
    try:
        workouts_file = os.path.join(self.base_dir, 'saved_workouts', 'workout_sessions.json')
        
        if not os.path.exists(workouts_file):
            return False
            
        with open(workouts_file, 'r') as f:
            workouts = json.load(f)
        
        # Find and update the session
        for workout in workouts:
            if workout.get('id') == session_id:
                workout.update(update_data)
                break
        
        # Save updated workouts
        with open(workouts_file, 'w') as f:
            json.dump(workouts, f, indent=4)
            
        return True
        
    except Exception as e:
        print(f"Error updating workout session: {str(e)}")
        return False

def get_workout_history(self, user_id):
    """Get workout history for a specific user"""
    try:
        workouts_file = os.path.join(self.base_dir, 'saved_workouts', 'workout_sessions.json')
        
        if not os.path.exists(workouts_file):
            return []
            
        with open(workouts_file, 'r') as f:
            workouts = json.load(f)
        
        # Filter workouts for the specific user
        user_workouts = [w for w in workouts if w.get('user_id') == user_id]
        
        # Sort by start time, most recent first
        user_workouts.sort(key=lambda x: x.get('start_time', ''), reverse=True)
        
        return user_workouts
        
    except Exception as e:
        print(f"Error getting workout history: {str(e)}")
        return []

def get_user(email: str):
    """Get a user by email"""
    print(f"[Database] Attempting to get user: {email}")
    
    if not validate_email(email):
        print("[Database] Invalid email format")
        return None
    
    user_db = load_user_database()
    if not user_db:
        print("[Database] User database is empty")
        return None
    
    user = user_db.get(email)
    if not user:
        print(f"[Database] User not found: {email}")
        return None
    
    print(f"[Database] User found: {email}")
    return user
