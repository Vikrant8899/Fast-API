# API Examples & Testing Guide

## 🚀 Starting the Server

```bash
uvicorn main:app --reload
```

The `--reload` flag automatically restarts the server when you change code (great for development).

Server will be available at: `http://localhost:8000`

---

## 📖 Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly from the browser using these interfaces!

---

## 🧪 cURL Examples

### Basic Endpoints

#### 1. Home Page
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "Welcome to FastAPI Learning Project!",
  "docs": "/docs",
  "features": ["Dependency Injection", "Middleware", "SQLite Database", "CRUD Operations"]
}
```

#### 2. Health Check (Dependency Injection Demo)
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "total_users": 0
}
```

---

## 👥 User CRUD Operations

### Create Users

#### Create User 1
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "username": "alice",
    "full_name": "Alice Wonder"
  }'
```

#### Create User 2
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@example.com",
    "username": "bob",
    "full_name": "Bob Builder"
  }'
```

#### Create User 3
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "charlie@example.com",
    "username": "charlie",
    "full_name": "Charlie Chaplin"
  }'
```

Expected response (example):
```json
{
  "email": "alice@example.com",
  "username": "alice",
  "full_name": "Alice Wonder",
  "id": 1,
  "is_active": true,
  "created_at": "2026-10-04T10:30:00.000000",
  "updated_at": null
}
```

#### Test Validation (should fail)
```bash
# Duplicate email
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "username": "alice2",
    "full_name": "Another Alice"
  }'
```

Expected error:
```json
{
  "detail": "Email already registered"
}
```

---

### Read Users

#### Get All Users
```bash
curl http://localhost:8000/users/
```

#### Get All Users with Pagination
```bash
# First page (skip 0, get 2 users)
curl "http://localhost:8000/users/?skip=0&limit=2"

# Second page (skip 2, get 2 users)
curl "http://localhost:8000/users/?skip=2&limit=2"
```

#### Search Users
```bash
# Search by name
curl "http://localhost:8000/users/?search=alice"

# Search by email
curl "http://localhost:8000/users/?search=example.com"
```

#### Get Specific User
```bash
curl http://localhost:8000/users/1
```

#### Get Non-Existent User (should fail)
```bash
curl http://localhost:8000/users/999
```

Expected error:
```json
{
  "detail": "User with id 999 not found"
}
```

---

### Update Users

#### Update User's Full Name
```bash
curl -X PATCH http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Alice in Wonderland"
  }'
```

#### Update Multiple Fields
```bash
curl -X PATCH http://localhost:8000/users/2 \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Robert The Builder",
    "is_active": false
  }'
```

#### Deactivate a User
```bash
curl -X PATCH http://localhost:8000/users/3 \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
```

---

### Delete Users

#### Delete a User
```bash
curl -X DELETE http://localhost:8000/users/3
```

Note: Returns status 204 (No Content) on success.

#### Try to Delete Again (should fail)
```bash
curl -X DELETE http://localhost:8000/users/3
```

Expected error:
```json
{
  "detail": "User with id 3 not found"
}
```

---

## 🔒 Protected Endpoints (Dependency Injection for Security)

### Without API Key (should fail)
```bash
curl http://localhost:8000/secure/users/
```

Expected error:
```json
{
  "detail": "Invalid or missing API key"
}
```

### With Correct API Key (should work)
```bash
curl http://localhost:8000/secure/users/ \
  -H "X-API-Key: secret-key-123"
```

### With Wrong API Key (should fail)
```bash
curl http://localhost:8000/secure/users/ \
  -H "X-API-Key: wrong-key"
```

---

## 🎓 Learning Examples

### Dependency Chain Example
```bash
curl "http://localhost:8000/examples/dependency-chain?skip=5&limit=10&search=test"
```

This demonstrates:
- Multiple dependencies working together
- Query parameter validation
- Database session injection

---

## 🕐 Middleware in Action

### Check Response Timing
```bash
curl -i http://localhost:8000/health
```

Look for the `X-Process-Time` header in the response!

Example:
```
HTTP/1.1 200 OK
content-type: application/json
x-process-time: 0.0023
```

### CORS Headers
```bash
curl -i -X OPTIONS http://localhost:8000/users/
```

You'll see CORS headers added by the middleware:
```
access-control-allow-origin: *
access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
access-control-allow-headers: *
```

---

## 🐍 Python Client Example

You can also interact with the API using Python:

```python
import requests

BASE_URL = "http://localhost:8000"

# Create a user
response = requests.post(
    f"{BASE_URL}/users/",
    json={
        "email": "dave@example.com",
        "username": "dave",
        "full_name": "Dave Developer"
    }
)
print(response.json())

# Get all users
response = requests.get(f"{BASE_URL}/users/")
users = response.json()
print(f"Total users: {len(users)}")

# Search users
response = requests.get(f"{BASE_URL}/users/?search=dave")
print(response.json())

# Update user
response = requests.patch(
    f"{BASE_URL}/users/1",
    json={"full_name": "Updated Name"}
)
print(response.json())

# Delete user
response = requests.delete(f"{BASE_URL}/users/1")
print(f"Status: {response.status_code}")

# Protected endpoint
response = requests.get(
    f"{BASE_URL}/secure/users/",
    headers={"X-API-Key": "secret-key-123"}
)
print(response.json())
```

---

## 🧪 Testing Scenarios

### Scenario 1: Complete User Lifecycle
```bash
# 1. Create user
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": "testuser", "full_name": "Test User"}'

# 2. Verify creation
curl http://localhost:8000/users/1

# 3. Update user
curl -X PATCH http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Updated Test User"}'

# 4. Verify update
curl http://localhost:8000/users/1

# 5. Delete user
curl -X DELETE http://localhost:8000/users/1

# 6. Verify deletion (should fail)
curl http://localhost:8000/users/1
```

### Scenario 2: Pagination Testing
```bash
# Create 10 users (run this 10 times with different data)
for i in {1..10}; do
  curl -X POST http://localhost:8000/users/ \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"user${i}@example.com\", \"username\": \"user${i}\", \"full_name\": \"User ${i}\"}"
done

# Test pagination
curl "http://localhost:8000/users/?skip=0&limit=3"  # First 3
curl "http://localhost:8000/users/?skip=3&limit=3"  # Next 3
curl "http://localhost:8000/users/?skip=6&limit=3"  # Next 3
```

### Scenario 3: Validation Testing
```bash
# Invalid email
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email": "not-an-email", "username": "test"}'

# Missing required field
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test"}'

# Limit too high (max is 100)
curl "http://localhost:8000/users/?limit=101"

# Skip negative (must be >= 0)
curl "http://localhost:8000/users/?skip=-1"
```

---

## 🔍 Monitoring & Debugging

### View Database File
```bash
# Check if database exists
ls -lh fastapi_learning.db

# Query database directly (requires sqlite3)
sqlite3 fastapi_learning.db "SELECT * FROM users;"
```

### Watch Logs
When the server is running with `--reload`, you'll see:
- Request timing logs from middleware
- Database session creation/closure logs (if using `get_db_with_logging`)
- HTTP request logs

---

## 💡 Tips & Tricks

### Using jq for Pretty JSON
```bash
# Install jq: brew install jq (macOS)

curl http://localhost:8000/users/ | jq .
```

### Save Response to File
```bash
curl http://localhost:8000/users/ > users.json
```

### Test with Different HTTP Methods
```bash
# GET
curl -X GET http://localhost:8000/users/1

# POST
curl -X POST http://localhost:8000/users/ -d '...'

# PATCH
curl -X PATCH http://localhost:8000/users/1 -d '...'

# DELETE
curl -X DELETE http://localhost:8000/users/1
```

### View Full Response Headers
```bash
curl -v http://localhost:8000/health
```

---

## 🎯 Challenge Exercises

Try implementing these yourself:

1. **Add a new field**: Add an `age` field to the User model
2. **Create a new endpoint**: Add `/users/stats` that returns user statistics
3. **Add filtering**: Filter users by `is_active` status
4. **Custom middleware**: Create middleware that logs the request body
5. **New dependency**: Create a dependency that validates user age
6. **Batch operations**: Add an endpoint to create multiple users at once

---

## 📚 Reference

### HTTP Status Codes Used
- `200 OK`: Successful GET/PATCH requests
- `201 Created`: Successful POST requests
- `204 No Content`: Successful DELETE requests
- `400 Bad Request`: Validation errors
- `403 Forbidden`: Invalid API key
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Request body validation failed
- `503 Service Unavailable`: Database connection failed

### Common Headers
- `Content-Type: application/json`: For sending JSON data
- `X-API-Key: secret-key-123`: For authentication
- `X-Process-Time`: Added by timing middleware

---

Happy testing! 🎉
