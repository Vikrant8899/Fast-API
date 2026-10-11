# FastAPI Learning Project

A comprehensive FastAPI project demonstrating advanced concepts including dependency injection, middleware, and SQLite database operations.

## 📚 What You'll Learn

### 1. **Dependency Injection**
- Database session injection (`get_db`)
- Custom dependencies (API key validation, pagination)
- Class-based dependencies (`CommonQueryParams`)
- Dependency chaining

### 2. **Middleware**
- Custom timing middleware
- Request logging middleware
- CORS configuration
- Understanding middleware execution order

### 3. **Database Operations**
- SQLite with SQLAlchemy
- CRUD operations (Create, Read, Update, Delete)
- Database models vs Pydantic schemas
- Query filtering and pagination

### 4. **API Best Practices**
- Request/response validation
- Proper HTTP status codes
- Error handling
- API documentation (automatic with FastAPI)

## 🚀 Getting Started

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

## 📖 Project Structure

```
.
├── main.py           # Main application with routes
├── database.py       # Database configuration and session management
├── models.py         # SQLAlchemy database models
├── schemas.py        # Pydantic validation schemas
├── crud.py           # Database CRUD operations
├── dependencies.py   # Custom dependency functions
├── middleware.py     # Custom middleware
└── requirements.txt  # Python dependencies
```

## 🎯 Key Concepts Explained

### Dependency Injection

FastAPI's dependency injection system allows you to:
- Reuse code across endpoints
- Share database connections
- Implement authentication/authorization
- Handle common query parameters

**Example:**
```python
@app.get("/users/")
def list_users(
    db: Session = Depends(get_db),  # Database session injected
    commons: CommonQueryParams = Depends()  # Common params injected
):
    return crud.get_users(db, skip=commons.skip, limit=commons.limit)
```

### Middleware

Middleware processes requests before they reach your endpoints and responses before they're sent to clients.

**Order of execution:**
1. Request comes in
2. Middleware processes request (in order added)
3. Route handler executes
4. Middleware processes response (in reverse order)
5. Response sent to client

**Example use cases:**
- Request logging
- Performance timing
- Authentication
- CORS headers
- Request/response modification

### Database Pattern

**Three-layer architecture:**
1. **Models** (`models.py`): SQLAlchemy models define database schema
2. **Schemas** (`schemas.py`): Pydantic models validate API data
3. **CRUD** (`crud.py`): Business logic for database operations

This separation keeps your code organized and testable.

## 🧪 Try These Endpoints

### Basic Endpoints

1. **Home**
   ```bash
   curl http://localhost:8000/
   ```

2. **Health Check** (uses dependency injection)
   ```bash
   curl http://localhost:8000/health
   ```

### User CRUD Operations

3. **Create a User**
   ```bash
   curl -X POST http://localhost:8000/users/ \
     -H "Content-Type: application/json" \
     -d '{
       "email": "alice@example.com",
       "username": "alice",
       "full_name": "Alice Wonder"
     }'
   ```

4. **List Users** (with pagination)
   ```bash
   curl http://localhost:8000/users/?skip=0&limit=10
   ```

5. **Search Users**
   ```bash
   curl http://localhost:8000/users/?search=alice
   ```

6. **Get Specific User**
   ```bash
   curl http://localhost:8000/users/1
   ```

7. **Update User** (partial update)
   ```bash
   curl -X PATCH http://localhost:8000/users/1 \
     -H "Content-Type: application/json" \
     -d '{
       "full_name": "Alice in Wonderland"
     }'
   ```

8. **Delete User**
   ```bash
   curl -X DELETE http://localhost:8000/users/1
   ```

### Protected Endpoint

9. **Secure Endpoint** (requires API key)
   ```bash
   curl http://localhost:8000/secure/users/ \
     -H "X-API-Key: secret-key-123"
   ```

### Learning Examples

10. **Dependency Chain Example**
    ```bash
    curl http://localhost:8000/examples/dependency-chain?skip=0&limit=5&search=test
    ```

## 🔍 Understanding the Code

### How Dependency Injection Works

When you write:
```python
def get_users(db: Session = Depends(get_db)):
    ...
```

FastAPI:
1. Recognizes `Depends(get_db)`
2. Calls `get_db()` function
3. Injects the result into your route function
4. Automatically closes the database session when done

### Custom Dependencies

**Function-based:**
```python
async def get_api_key(x_api_key: str = Header(None)):
    if x_api_key != "secret-key-123":
        raise HTTPException(status_code=403)
    return x_api_key
```

**Class-based:**
```python
class CommonQueryParams:
    def __init__(self, skip: int = 0, limit: int = 10):
        self.skip = skip
        self.limit = limit
```

### Middleware Structure

```python
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Before request processing
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # After request processing
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
```

## 🎓 Learning Path

1. **Start Simple**: Run the app and try the `/health` endpoint
2. **Create Users**: Use POST `/users/` to create a few test users
3. **Explore CRUD**: Try all CRUD operations
4. **Test Pagination**: Use different skip/limit values
5. **Try Search**: Search for users by name or email
6. **Protected Routes**: Test the secure endpoint with/without API key
7. **Watch Middleware**: Notice the `X-Process-Time` header in responses
8. **Read the Code**: Explore each file and understand the patterns

## 🔧 Customization Ideas

Try extending the project:
- Add authentication with JWT tokens
- Add more models (Posts, Comments, etc.)
- Implement role-based access control
- Add caching middleware
- Create custom validation dependencies
- Add background tasks
- Implement WebSockets

## 📝 Notes

- The SQLite database file `fastapi_learning.db` is created automatically
- Middleware logging helps you see request flow
- Check `/docs` for interactive API documentation
- All endpoints include proper error handling
- Response models ensure consistent API output

## 🤝 Next Steps

After mastering these concepts, explore:
- Async database drivers (like `databases` or `asyncpg`)
- Testing with `pytest` and `TestClient`
- Background tasks with Celery
- File uploads and streaming responses
- WebSocket connections
- GraphQL integration
