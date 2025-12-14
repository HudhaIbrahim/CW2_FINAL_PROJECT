from app.data.db import connect_database

class User:
    """User data model."""
    def __init__(self, username, password_hash, role='user', id=None):
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.id = id
    
    def __str__(self):
        return f"User(id={self.id}, username={self.username}, role={self.role})"

    @staticmethod # static method allows calling without instantiating the class
    def get_user_by_username(username):
        """Retrieve user by username."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ?",(username,) )
        user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def insert_user(username, password_hash, role='user'):
        """Insert new user."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role)
        )
        conn.commit()
        conn.close()