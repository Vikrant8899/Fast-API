"""
CRUD operations (Create, Read, Update, Delete) for users.
This layer separates database logic from API routes.
Uses raw SQL queries instead of ORM.
"""
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert sqlite3.Row to dictionary"""
    return dict(row) if row else None


def get_user(conn: sqlite3.Connection, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a single user by ID using raw SQL.
    
    SQL: SELECT * FROM users WHERE id = ?
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    return row_to_dict(row)


def get_user_by_email(conn: sqlite3.Connection, email: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by email using raw SQL.
    
    SQL: SELECT * FROM users WHERE email = ?
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()
    return row_to_dict(row)


def get_user_by_username(conn: sqlite3.Connection, username: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by username using raw SQL.
    
    SQL: SELECT * FROM users WHERE username = ?
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    return row_to_dict(row)


def get_users(
    conn: sqlite3.Connection, 
    skip: int = 0, 
    limit: int = 10,
    search: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get a list of users with pagination and optional search using raw SQL.
    
    Args:
        conn: Database connection
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        search: Optional search term to filter by username, email, or full_name
    
    SQL Examples:
    - Without search: SELECT * FROM users LIMIT ? OFFSET ?
    - With search: SELECT * FROM users WHERE username LIKE ? OR email LIKE ? OR full_name LIKE ? LIMIT ? OFFSET ?
    """
    cursor = conn.cursor()
    
    if search:
        # Search in username, email, and full_name
        search_pattern = f"%{search}%"
        cursor.execute(
            """
            SELECT * FROM users 
            WHERE username LIKE ? OR email LIKE ? OR full_name LIKE ?
            LIMIT ? OFFSET ?
            """,
            (search_pattern, search_pattern, search_pattern, limit, skip)
        )
    else:
        # No search filter
        cursor.execute(
            "SELECT * FROM users LIMIT ? OFFSET ?",
            (limit, skip)
        )
    
    rows = cursor.fetchall()
    return [row_to_dict(row) for row in rows]


def create_user(conn: sqlite3.Connection, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new user using raw SQL INSERT.
    
    SQL: INSERT INTO users (email, username, full_name) VALUES (?, ?, ?)
    
    Returns the created user with its generated ID.
    """
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO users (email, username, full_name)
        VALUES (?, ?, ?)
        """,
        (user_data["email"], user_data["username"], user_data.get("full_name"))
    )
    
    conn.commit()
    
    # Get the ID of the newly created user
    user_id = cursor.lastrowid
    
    # Fetch and return the complete user record
    return get_user(conn, user_id)


def update_user(
    conn: sqlite3.Connection, 
    user_id: int, 
    update_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Update an existing user using raw SQL UPDATE.
    Only updates fields that are provided (not None).
    
    SQL: UPDATE users SET field1 = ?, field2 = ?, updated_at = ? WHERE id = ?
    
    Returns the updated user or None if user not found.
    """
    # Check if user exists
    user = get_user(conn, user_id)
    if not user:
        return None
    
    # Build dynamic UPDATE query for provided fields
    update_fields = []
    update_values = []
    
    for field, value in update_data.items():
        if value is not None:  # Only update fields that are provided
            update_fields.append(f"{field} = ?")
            update_values.append(value)
    
    if not update_fields:
        # No fields to update
        return user
    
    # Add updated_at timestamp
    update_fields.append("updated_at = ?")
    update_values.append(datetime.utcnow().isoformat())
    
    # Add user_id for WHERE clause
    update_values.append(user_id)
    
    # Build and execute UPDATE query
    query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
    
    cursor = conn.cursor()
    cursor.execute(query, update_values)
    conn.commit()
    
    # Fetch and return the updated user
    return get_user(conn, user_id)


def delete_user(conn: sqlite3.Connection, user_id: int) -> bool:
    """
    Delete a user using raw SQL DELETE.
    
    SQL: DELETE FROM users WHERE id = ?
    
    Returns True if deleted, False if user not found.
    """
    # Check if user exists
    user = get_user(conn, user_id)
    if not user:
        return False
    
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM users WHERE id = ?",
        (user_id,)
    )
    conn.commit()
    
    return True


def get_user_count(conn: sqlite3.Connection) -> int:
    """
    Get total count of users using raw SQL COUNT.
    
    SQL: SELECT COUNT(*) FROM users
    """
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users")
    result = cursor.fetchone()
    return result["count"]
