"""
FastAPI Learning Project
========================
This project demonstrates:
- Dependency Injection (database connections, auth, pagination)
- Middleware (timing, CORS, logging)
- SQLite database with raw SQL queries
- CRUD operations
- Request/Response validation with Pydantic
"""
# just as comment
from fastapi import FastAPI, Depends, HTTPException, status
import sqlite3
from typing import List

# Import our modules
import crud
from database import get_db, init_db
from dependencies import get_api_key, CommonQueryParams
from middleware import setup_middleware
import schemas

# Create FastAPI app
app = FastAPI(
    title="FastAPI Learning Project",
    description="Learn dependency injection, middleware, and database operations with raw SQL",
    version="1.0.0"
)

# Setup middleware
setup_middleware(app)


@app.on_event("startup")
def on_startup():
    """
    Initialize database on application startup.
    This is an event handler that runs when the app starts.
    """
    print("🚀 Starting up...")
    init_db()
    print("✅ Database initialized")


@app.get("/")
def home():
    """
    Root endpoint - no dependencies
    """
    return {
        "message": "Welcome to FastAPI Learning Project!",
        "docs": "/docs",
        "features": [
            "Dependency Injection",
            "Middleware",
            "SQLite Database with Raw SQL",
            "CRUD Operations"
        ]
    }


@app.get("/health")
def health_check(conn: sqlite3.Connection = Depends(get_db)):
    """
    Health check endpoint.
    Demonstrates basic dependency injection with database connection.
    """
    try:
        # Test database connection
        user_count = crud.get_user_count(conn)
        return {
            "status": "healthy",
            "database": "connected",
            "total_users": user_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {str(e)}"
        )


# ==================== USER CRUD ENDPOINTS ====================

@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: schemas.UserCreate,
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Create a new user using raw SQL INSERT.
    
    Demonstrates:
    - Dependency injection for database connection
    - Request validation with Pydantic schema
    - Response model for consistent API responses
    
    SQL: INSERT INTO users (email, username, full_name) VALUES (?, ?, ?)
    """
    # Check if user already exists
    if crud.get_user_by_email(conn, email=user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if crud.get_user_by_username(conn, username=user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    user_data = user.model_dump()
 
    return crud.create_user(conn, user_data)


@app.get("/users/", response_model=List[schemas.UserResponse])
def list_users(
    commons: CommonQueryParams = Depends(),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    List users with pagination and search using raw SQL.
    
    Demonstrates:
    - Class-based dependency for common query parameters
    - Multiple dependencies in a single endpoint
    - Pagination pattern with LIMIT and OFFSET
    
    SQL: SELECT * FROM users LIMIT ? OFFSET ?
    Or with search: SELECT * FROM users WHERE username LIKE ? ... LIMIT ? OFFSET ?
    
    Query parameters:
    - skip: number of records to skip (default: 0)
    - limit: max records to return (default: 10, max: 100)
    - search: optional search term
    """
    users = crud.get_users(
        conn=conn,
        skip=commons.skip,
        limit=commons.limit,
        search=commons.search
    )
    return users


@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(
    user_id: int,
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Get a specific user by ID using raw SQL.
    
    SQL: SELECT * FROM users WHERE id = ?
    
    Path parameters are automatically validated.
    """
    db_user = crud.get_user(conn=conn, user_id=user_id)
    
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return db_user


@app.patch("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Update a user (partial update) using raw SQL UPDATE.
    
    SQL: UPDATE users SET field1 = ?, field2 = ?, updated_at = ? WHERE id = ?
    
    Only provided fields will be updated.
    """
    update_data = user_update.model_dump(exclude_unset=True)
    db_user = crud.update_user(conn=conn, user_id=user_id, update_data=update_data)
    
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return db_user


@app.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Delete a user using raw SQL DELETE.
    
    SQL: DELETE FROM users WHERE id = ?
    
    Returns 204 No Content on success.
    """
    success = crud.delete_user(conn=conn, user_id=user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    return {
        "message":'user deleted'
    }


# ==================== PROTECTED ENDPOINTS ====================

@app.get("/secure/users/", response_model=List[schemas.UserResponse])
def list_users_secure(
    conn: sqlite3.Connection = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """
    Protected endpoint requiring API key.
    
    Demonstrates:
    - Security through dependency injection
    - Multiple dependencies including authentication
    
    To access: add header `X-API-Key: secret-key-123`
    """
    return crud.get_users(conn=conn, limit=100)


# ==================== EXAMPLES & LEARNING ====================

@app.get("/examples/dependency-chain")
def dependency_chain_example(
    commons: CommonQueryParams = Depends(),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Example showing multiple dependencies in action.
    
    Try: /examples/dependency-chain?skip=0&limit=5&search=test
    """
    return {
        "message": "Dependencies resolved successfully!",
        "query_params": {
            "skip": commons.skip,
            "limit": commons.limit,
            "search": commons.search
        },
        "database_connection_id": id(conn),
        "explanation": "Both CommonQueryParams and database connection were injected"
    }


@app.get("/examples/raw-sql-demo")
def raw_sql_demo(conn: sqlite3.Connection = Depends(get_db)):
    """
    Demonstrates raw SQL queries in action.
    Shows the actual SQL being executed.
    """
    cursor = conn.cursor()
    
    # Example: Count users
    cursor.execute("SELECT COUNT(*) as count FROM users")
    count = cursor.fetchone()["count"]
    
    # Example: Get table info
    cursor.execute("PRAGMA table_info(users)")
    columns = [dict(row) for row in cursor.fetchall()]
    
    return {
        "message": "Raw SQL demonstration",
        "total_users": count,
        "table_structure": columns,
        "sql_examples": {
            "count": "SELECT COUNT(*) as count FROM users",
            "list_all": "SELECT * FROM users",
            "find_by_id": "SELECT * FROM users WHERE id = ?",
            "search": "SELECT * FROM users WHERE username LIKE '%search%'",
            "insert": "INSERT INTO users (email, username, full_name) VALUES (?, ?, ?)",
            "update": "UPDATE users SET full_name = ? WHERE id = ?",
            "delete": "DELETE FROM users WHERE id = ?"
        }
    }

