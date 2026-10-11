# 📝 FastAPI Concepts Cheat Sheet

Quick reference for dependency injection, middleware, and database operations.

---

## 🎯 Dependency Injection

### Basic Function Dependency
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
def list_users(db: Session = Depends(get_db)):
    return crud.get_users(db)
```

### Class-Based Dependency
```python
class CommonParams:
    def __init__(self, skip: int = 0, limit: int = 10):
        self.skip = skip
        self.limit = limit

@app.get("/items/")
def list_items(commons: CommonParams = Depends()):
    # Use commons.skip and commons.limit
    pass
```

### Dependency with Validation
```python
async def verify_token(token: str = Header(...)):
    if token != "valid-token":
        raise HTTPException(status_code=403)
    return token

@app.get("/protected/")
def protected_route(token: str = Depends(verify_token)):
    return {"message": "authenticated"}
```

### Nested Dependencies
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db)):
    # Uses get_db dependency
    return db.query(User).first()

@app.get("/me")
def read_me(user: User = Depends(get_current_user)):
    # Uses get_current_user which uses get_db
    return user
```

---

## 🔄 Middleware

### Custom Middleware Template
```python
from starlette.middleware.base import BaseHTTPMiddleware

class MyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # BEFORE request processing
        print(f"Before: {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # AFTER request processing
        print(f"After: {response.status_code}")
        
        return response

# Add to app
app.add_middleware(MyMiddleware)
```

### CORS Middleware
```python
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Request Timing
```python
import time

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        response.headers["X-Duration"] = str(duration)
        return response
```

### Request Logging
```python
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f"{request.method} {request.url}")
        response = await call_next(request)
        print(f"Status: {response.status_code}")
        return response
```

---

## 💾 Database Operations

### Setup
```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
```

### Model Definition
```python
# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
```

### Pydantic Schema
```python
# schemas.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)
```

### CRUD Operations
```python
# Create
def create_user(db: Session, user: UserCreate):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Read
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Read Multiple
def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()

# Update
def update_user(db: Session, user_id: int, update_data: dict):
    db_user = get_user(db, user_id)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    return db_user

# Delete
def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    db.delete(db_user)
    db.commit()
```

---

## 🛣️ Route Patterns

### Basic GET
```python
@app.get("/items/")
def list_items():
    return [{"id": 1, "name": "Item 1"}]
```

### GET with Path Parameter
```python
@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"id": item_id}
```

### GET with Query Parameters
```python
@app.get("/items/")
def list_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

### POST with Body
```python
@app.post("/items/", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db, item)
```

### PATCH (Partial Update)
```python
@app.patch("/items/{item_id}")
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    return crud.update_item(db, item_id, item)
```

### DELETE
```python
@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    crud.delete_item(db, item_id)
```

---

## 🎨 Request/Response Patterns

### Response Model
```python
@app.get("/users/", response_model=List[UserResponse])
def list_users():
    return users
```

### Status Code
```python
@app.post("/users/", status_code=status.HTTP_201_CREATED)
def create_user():
    return user
```

### Error Handling
```python
from fastapi import HTTPException

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = find_user(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User {user_id} not found"
        )
    return user
```

### Headers
```python
from fastapi import Header

@app.get("/items/")
def read_items(user_agent: str = Header(None)):
    return {"User-Agent": user_agent}
```

---

## 🔐 Authentication Patterns

### API Key in Header
```python
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != "secret-key":
        raise HTTPException(status_code=403)
    return x_api_key

@app.get("/protected/")
def protected(api_key: str = Depends(verify_api_key)):
    return {"message": "authenticated"}
```

### Bearer Token
```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Depends(security)):
    token = credentials.credentials
    if token != "valid-token":
        raise HTTPException(status_code=403)
    return token
```

---

## 📦 Query Parameter Validation

```python
from fastapi import Query

@app.get("/items/")
def list_items(
    skip: int = Query(0, ge=0),  # >= 0
    limit: int = Query(10, ge=1, le=100),  # 1 to 100
    search: str = Query(None, min_length=3, max_length=50)
):
    return {"skip": skip, "limit": limit, "search": search}
```

---

## 🧪 Common HTTP Status Codes

```python
from fastapi import status

# Success
status.HTTP_200_OK              # GET success
status.HTTP_201_CREATED         # POST success
status.HTTP_204_NO_CONTENT      # DELETE success

# Client Errors
status.HTTP_400_BAD_REQUEST     # Invalid input
status.HTTP_401_UNAUTHORIZED    # Not authenticated
status.HTTP_403_FORBIDDEN       # Authenticated but no permission
status.HTTP_404_NOT_FOUND       # Resource not found
status.HTTP_422_UNPROCESSABLE_ENTITY  # Validation error

# Server Errors
status.HTTP_500_INTERNAL_SERVER_ERROR
status.HTTP_503_SERVICE_UNAVAILABLE
```

---

## 🔄 SQLAlchemy Query Patterns

### Basic Query
```python
db.query(User).all()  # Get all
db.query(User).first()  # Get first
db.query(User).count()  # Count
```

### Filter
```python
db.query(User).filter(User.id == 1).first()
db.query(User).filter(User.email == "test@example.com").first()
db.query(User).filter(User.is_active == True).all()
```

### Multiple Filters
```python
db.query(User).filter(
    User.is_active == True,
    User.email.contains("example.com")
).all()
```

### OR Condition
```python
from sqlalchemy import or_

db.query(User).filter(
    or_(
        User.username.contains(search),
        User.email.contains(search)
    )
).all()
```

### Pagination
```python
db.query(User).offset(skip).limit(limit).all()
```

### Ordering
```python
db.query(User).order_by(User.created_at.desc()).all()
db.query(User).order_by(User.username.asc()).all()
```

---

## 🚀 Startup/Shutdown Events

```python
@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    # Initialize database
    # Connect to external services

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down...")
    # Close connections
    # Cleanup resources
```

---

## 🐛 Debugging Tips

### Print Request Body
```python
@app.post("/debug/")
async def debug_request(request: Request):
    body = await request.json()
    print(f"Received: {body}")
    return body
```

### Inspect Database Session
```python
def get_db():
    db = SessionLocal()
    print(f"Session created: {id(db)}")
    try:
        yield db
    finally:
        print(f"Session closed: {id(db)}")
        db.close()
```

### Log Middleware
```python
class DebugMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        print(f"Path: {request.url.path}")
        print(f"Method: {request.method}")
        print(f"Headers: {request.headers}")
        response = await call_next(request)
        return response
```

---

## 📚 Quick Reference Commands

```bash
# Start server
uvicorn main:app --reload

# Start on different port
uvicorn main:app --reload --port 8001

# View docs
open http://localhost:8000/docs

# Test endpoint
curl http://localhost:8000/endpoint

# POST request
curl -X POST http://localhost:8000/endpoint \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'

# With header
curl http://localhost:8000/endpoint \
  -H "X-API-Key: secret-key"
```

---

## 💡 Best Practices

✅ **Do:**
- Use dependency injection for shared logic
- Separate models (DB) from schemas (API)
- Use CRUD layer for database operations
- Validate inputs with Pydantic
- Use appropriate HTTP status codes
- Close database sessions properly

❌ **Don't:**
- Mix database logic in route handlers
- Expose sensitive data in responses
- Forget to handle errors
- Use synchronous code in async functions
- Hardcode configuration values

---

**Quick Access:**
- Full Tutorial: `TUTORIAL.md`
- Examples: `EXAMPLES.md`
- Quick Start: `QUICKSTART.md`
