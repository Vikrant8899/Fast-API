# FastAPI Advanced Concepts Tutorial

## 🎯 Overview

This tutorial will guide you through the advanced FastAPI concepts you requested:
1. **Dependency Injection**
2. **Middleware**
3. **Database Operations with SQLite**

Let's explore each concept in detail!

---

## 1️⃣ Dependency Injection

### What is Dependency Injection?

Dependency Injection (DI) is a design pattern where you declare what your code needs, and the framework provides it automatically. In FastAPI, this is incredibly powerful and clean.

### Why Use It?

- **Code Reusability**: Write once, use everywhere
- **Testability**: Easy to mock dependencies in tests
- **Clean Code**: No global variables or tight coupling
- **Automatic Cleanup**: Resources are properly managed

### Types of Dependencies in This Project

#### 1. Database Session Dependency (`get_db`)

**Location**: `database.py`

```python
def get_db():
    db = SessionLocal()
    try:
        yield db  # Provides the session to your route
    finally:
        db.close()  # Always closes, even if errors occur
```

**How it works**:
- FastAPI calls `get_db()` before your route runs
- The `yield` statement provides the database session
- After your route completes, the `finally` block runs
- The session is automatically closed

**Usage**:
```python
@app.get("/users/")
def list_users(db: Session = Depends(get_db)):
    # 'db' is automatically provided and closed
    return crud.get_users(db)
```

#### 2. Class-Based Dependencies (`CommonQueryParams`)

**Location**: `dependencies.py`

```python
class CommonQueryParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        search: Optional[str] = Query(None)
    ):
        self.skip = skip
        self.limit = limit
        self.search = search
```

**Why use a class?**
- Groups related parameters together
- Reusable across multiple endpoints
- Validates parameters automatically
- Clean and organized

**Usage**:
```python
@app.get("/users/")
def list_users(
    commons: CommonQueryParams = Depends(),  # No arguments needed!
    db: Session = Depends(get_db)
):
    # commons.skip, commons.limit, commons.search are all available
    return crud.get_users(db, skip=commons.skip, limit=commons.limit)
```

#### 3. Security Dependencies (`get_api_key`)

**Location**: `dependencies.py`

```python
async def get_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != "secret-key-123":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key
```

**Usage**:
```python
@app.get("/secure/users/")
def secure_endpoint(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)  # Automatically validates
):
    # This code only runs if API key is valid
    return crud.get_users(db)
```

#### 4. Dependency Chaining

You can have dependencies that depend on other dependencies!

```python
def get_db_with_logging(db: Session = Depends(get_db)):
    print(f"Database session created: {id(db)}")
    try:
        yield db
    finally:
        print(f"Database session closed: {id(db)}")
```

This dependency **depends on** `get_db`, adding logging on top.

### Dependency Best Practices

1. **Use `Depends()` for reusable logic**: Authentication, database connections, common parameters
2. **Keep dependencies simple**: Each dependency should do one thing well
3. **Chain dependencies**: Build complex behavior from simple pieces
4. **Use type hints**: FastAPI uses them to understand what to inject

---

## 2️⃣ Middleware

### What is Middleware?

Middleware is code that runs **before** and **after** every request. Think of it as a wrapper around your entire application.

### Request/Response Flow

```
Client Request
    ↓
Middleware 1 (before)
    ↓
Middleware 2 (before)
    ↓
Your Route Handler
    ↓
Middleware 2 (after)
    ↓
Middleware 1 (after)
    ↓
Client Response
```

### Middleware in This Project

#### 1. Timing Middleware

**Location**: `middleware.py`

```python
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process the request (your route runs here)
        response = await call_next(request)
        
        # Calculate and add timing
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
```

**What it does**:
- Measures how long each request takes
- Adds the time to response headers
- Logs the timing to console

**Try it**: Check the `X-Process-Time` header in any response!

#### 2. CORS Middleware

**Location**: `middleware.py` (setup_middleware function)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Which domains can access your API
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)
```

**What it does**:
- Allows cross-origin requests (from web browsers)
- Essential for frontend applications
- Configurable per your security needs

### When to Use Middleware

- **Logging**: Record all requests
- **Authentication**: Validate tokens globally
- **Performance Monitoring**: Track response times
- **CORS**: Enable browser access
- **Rate Limiting**: Prevent abuse
- **Request ID**: Track requests across services
- **Error Handling**: Catch and format errors consistently

### Creating Custom Middleware

Template:
```python
class MyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Code BEFORE route handler
        print(f"Request: {request.method} {request.url}")
        
        # Call the route handler
        response = await call_next(request)
        
        # Code AFTER route handler
        print(f"Response: {response.status_code}")
        
        return response
```

### Middleware Order Matters!

Middleware is executed in the order it's added:

```python
app.add_middleware(CORSMiddleware)      # Runs first (outermost)
app.add_middleware(TimingMiddleware)    # Runs second
app.add_middleware(LoggingMiddleware)   # Runs third (innermost)
```

---

## 3️⃣ Database with SQLite

### Architecture Overview

This project uses a **three-layer architecture**:

```
API Layer (main.py)
    ↓
Business Logic (crud.py)
    ↓
Database (models.py + database.py)
```

### Components

#### 1. Database Configuration (`database.py`)

```python
# Database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./fastapi_learning.db"

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
```

**Key Points**:
- `engine`: Manages database connections
- `SessionLocal`: Factory for creating database sessions
- `Base`: All models inherit from this

#### 2. Models (`models.py`)

Models define your database schema:

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Each Column means**:
- `primary_key`: Unique identifier
- `index`: Faster lookups
- `unique`: No duplicates allowed
- `nullable`: Can be NULL/None
- `default`: Default value if not provided

#### 3. Schemas (`schemas.py`)

Pydantic models validate API data:

```python
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
```

**Models vs Schemas**:
- **Models** (`models.py`): Database structure (SQLAlchemy)
- **Schemas** (`schemas.py`): API validation (Pydantic)

They're separate because:
- Database might have fields you don't expose via API
- API might accept fields that aren't stored directly
- Validation rules differ from storage rules

#### 4. CRUD Operations (`crud.py`)

CRUD = Create, Read, Update, Delete

**Create**:
```python
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Get the generated ID
    return db_user
```

**Read**:
```python
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()
```

**Update**:
```python
def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    db.commit()
    return db_user
```

**Delete**:
```python
def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    db.delete(db_user)
    db.commit()
```

### Database Session Lifecycle

```
Request comes in
    ↓
FastAPI calls get_db()
    ↓
SessionLocal() creates new session
    ↓
yield session to route handler
    ↓
Route handler uses session
    ↓
Route completes
    ↓
finally: block closes session
    ↓
Response sent
```

**Why this pattern?**
- Each request gets its own session
- Sessions are always closed (no leaks)
- Transactions are properly managed
- Works with dependency injection

---

## 🧪 Hands-On Exercises

### Exercise 1: Create Your First User

```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "johndoe",
    "full_name": "John Doe"
  }'
```

**What happens**:
1. FastAPI validates the JSON against `UserCreate` schema
2. Dependency injection provides database session
3. `create_user` CRUD function runs
4. User is saved to SQLite database
5. Response is validated against `UserResponse` schema
6. Database session automatically closes

### Exercise 2: Test Pagination

```bash
# Create multiple users first, then:
curl "http://localhost:8000/users/?skip=0&limit=5"
curl "http://localhost:8000/users/?skip=5&limit=5"
```

**What happens**:
1. `CommonQueryParams` dependency extracts query parameters
2. Validates: skip >= 0, limit between 1 and 100
3. Passes to CRUD function
4. SQL query uses OFFSET and LIMIT
5. Returns paginated results

### Exercise 3: Try the Secure Endpoint

```bash
# Without API key (should fail)
curl http://localhost:8000/secure/users/

# With API key (should work)
curl http://localhost:8000/secure/users/ \
  -H "X-API-Key: secret-key-123"
```

**What happens**:
1. Request hits secure endpoint
2. FastAPI resolves dependencies in order
3. `get_api_key` dependency checks header
4. If invalid: raises 403 error, route never runs
5. If valid: route handler executes normally

### Exercise 4: Watch Middleware in Action

```bash
# Make any request and check headers
curl -I http://localhost:8000/health
```

Look for `X-Process-Time` header showing request duration.

---

## 🎓 Key Takeaways

### Dependency Injection
- ✅ Declare what you need, FastAPI provides it
- ✅ Automatic cleanup and resource management
- ✅ Great for database sessions, auth, shared logic
- ✅ Testable and maintainable

### Middleware
- ✅ Runs on every request
- ✅ Perfect for logging, timing, CORS
- ✅ Wraps your entire application
- ✅ Order matters!

### Database
- ✅ Three-layer architecture (API → Logic → Database)
- ✅ Models for database, Schemas for API
- ✅ CRUD operations separate business logic
- ✅ Sessions managed automatically via DI

---

## 🚀 Next Steps

1. **Add more models**: Create `Post`, `Comment` models with relationships
2. **Implement JWT auth**: Replace simple API key with tokens
3. **Add background tasks**: Email notifications, async processing
4. **Write tests**: Use `TestClient` to test your API
5. **Add caching**: Redis or in-memory caching middleware
6. **File uploads**: Handle multipart form data
7. **WebSockets**: Real-time communication

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Starlette Middleware](https://www.starlette.io/middleware/)

---

## ❓ Common Questions

**Q: When should I use dependency injection vs regular function calls?**
A: Use DI for resources that need lifecycle management (database sessions, external connections) or shared logic that needs to run across many endpoints (auth, validation).

**Q: Can I have async dependencies?**
A: Yes! Just use `async def` instead of `def`.

**Q: How do I test code with dependencies?**
A: Override dependencies in tests using `app.dependency_overrides`.

**Q: Should middleware or dependencies handle authentication?**
A: Dependencies are better for authentication because they're more flexible and testable. Use middleware for global concerns like CORS or request logging.

**Q: What's the difference between `Session` and `SessionLocal`?**
A: `SessionLocal` is a factory (class) that creates `Session` instances.

---

Happy learning! 🎉
