import bcrypt
from app.data.db import connect_database
from app.data.users import User
from app.services.database_manager import DatabaseManager

class AuthManager:
    """Authentication and User Management Service
    """
    def __init__(self, db: DatabaseManager):
        self.db = db

    @staticmethod
    def register_user(username, password, role='user'):
        """Register new user with password hashing."""
        conn = connect_database() 
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, f"Username '{username}' already exists."
        
        # Hash password
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Insert new user into database
        User.insert_user(username, password_hash, role)
        return True, f"User '{username}' registered successfully."

    @staticmethod
    def validate_username(username):
        '''Validates the username format.'''
        if not username or len(username) < 3:
            return(False,"Username must be at least 3 characters long.")
        return (True, "is valid")

    @staticmethod
    def validate_password(password):
        '''Validates password strength.'''
        if not password or len(password) < 8:
            return (False, "Password must be at least 8 characters long.")
        
        has_upper = any(i.isupper() for i in password)
        has_lower = any(i.islower() for i in password)
        has_digit = any(i.isdigit() for i in password)
        
        if not has_upper:
            return (False, "Password must contain at least one uppercase letter.")
        if not has_lower:
            return (False, "Password must contain at least one lowercase letter.")
        if not has_digit:
            return (False, "Password must contain at least one digit.")
        
        return (True, "is valid")

    @staticmethod
    def login_user(username, password):
        """Authenticate user."""
        user = User.get_user_by_username(username)
        if not user:
            return False, "User not found."
        
        # Verify password
        stored_hash = user[2]  # password_hash column
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return True, f"Login successful!"
        return False, "Incorrect password."


