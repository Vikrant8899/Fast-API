"""
Database configuration and connection management.
This demonstrates dependency injection for database connections.
Uses raw SQL queries instead of ORM.
"""
import sqlite3
from contextlib import contextmanager

# SQLite database file
DATABASE_URL = "fastapi_learning.db"


def get_db_connection():
    """
    Create a database connection.
    Returns a connection with row_factory set to sqlite3.Row
    so we can access columns by name.
    """
    conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def get_db():
    """
    Dependency function that yields a database connection.
    This is a key example of dependency injection in FastAPI.
    
    The connection is automatically closed after the request completes,
    even if an exception occurs.
    """
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """
    Initialize the database by creating tables using raw SQL.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table with raw SQL
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            full_name TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    
    # Create indexes for better query performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_email 
        ON users(email)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_username 
        ON users(username)
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Database tables created successfully")
