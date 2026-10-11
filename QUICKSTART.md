# 🚀 Quick Start Guide

Get up and running with this FastAPI learning project in under 5 minutes!

---

## ⚡ Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
🚀 Starting up...
✅ Database initialized
```

### 3. Open Interactive Docs
Visit: **http://localhost:8000/docs**

This is your interactive API playground - you can test all endpoints right from the browser!

---

## 🎯 Your First API Call

### Option 1: Using the Browser (Easiest!)

1. Go to http://localhost:8000/docs
2. Click on `POST /users/`
3. Click "Try it out"
4. Enter:
```json
{
  "email": "alice@example.com",
  "username": "alice",
  "full_name": "Alice Wonder"
}
```
5. Click "Execute"

### Option 2: Using cURL (Terminal)

```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "username": "alice",
    "full_name": "Alice Wonder"
  }'
```

### Option 3: Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/users/",
    json={
        "email": "alice@example.com",
        "username": "alice",
        "full_name": "Alice Wonder"
    }
)
print(response.json())
```

---

## ✅ Verify It Works

### Get the user you just created:
```bash
curl http://localhost:8000/users/1
```

Should return:
```json
{
  "email": "alice@example.com",
  "username": "alice",
  "full_name": "Alice Wonder",
  "id": 1,
  "is_active": true,
  "created_at": "2026-10-04T...",
  "updated_at": null
}
```

---

## 🎓 Learning Journey (5 Steps)

### Step 1: Explore Basic Endpoints (2 min)
```bash
# Home page
curl http://localhost:8000/

# Health check (notice it uses dependency injection!)
curl http://localhost:8000/health
```

**🔍 What's happening?**
- The `/health` endpoint uses `get_db` dependency
- Database session is automatically provided and closed
- This is **Dependency Injection** in action!

---

### Step 2: CRUD Operations (5 min)

**Create** (C in CRUD):
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email": "bob@example.com", "username": "bob", "full_name": "Bob Builder"}'
```

**Read** (R in CRUD):
```bash
# Get all users
curl http://localhost:8000/users/

# Get specific user
curl http://localhost:8000/users/1
```

**Update** (U in CRUD):
```bash
curl -X PATCH http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Alice in Wonderland"}'
```

**Delete** (D in CRUD):
```bash
curl -X DELETE http://localhost:8000/users/2
```

---

### Step 3: Test Dependency Injection (3 min)

**Pagination** (uses `CommonQueryParams` dependency):
```bash
# Create several users first, then:
curl "http://localhost:8000/users/?skip=0&limit=2"
curl "http://localhost:8000/users/?skip=2&limit=2"
```

**Search** (also uses `CommonQueryParams`):
```bash
curl "http://localhost:8000/users/?search=alice"
```

**🔍 What's happening?**
- `skip`, `limit`, `search` are validated automatically
- They're packaged into a `CommonQueryParams` object
- FastAPI injects this object into your route handler
- This is **class-based dependency injection**!

---

### Step 4: Test Authentication (2 min)

**Without API key** (should fail):
```bash
curl http://localhost:8000/secure/users/
```

Response:
```json
{"detail": "Invalid or missing API key"}
```

**With correct API key** (should work):
```bash
curl http://localhost:8000/secure/users/ \
  -H "X-API-Key: secret-key-123"
```

**🔍 What's happening?**
- The `get_api_key` dependency validates the header
- If invalid, it raises an HTTPException
- Your route handler only runs if validation passes
- This is **security through dependency injection**!

---

### Step 5: Observe Middleware (1 min)

Check response headers:
```bash
curl -i http://localhost:8000/health
```

Look for:
```
X-Process-Time: 0.0023
```

**🔍 What's happening?**
- `TimingMiddleware` wraps every request
- It measures how long the request takes
- Adds the timing to response headers
- This is **middleware** in action!

---

## 🔥 Challenge: Create Your Own User

Try creating a user with your own information:

```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com",
    "username": "yourusername",
    "full_name": "Your Full Name"
  }'
```

Then retrieve it:
```bash
curl http://localhost:8000/users/
```

---

## 📚 What to Read Next

Now that you've tried the basics, dive deeper:

1. **TUTORIAL.md** - Detailed explanations of:
   - How dependency injection works
   - How middleware works
   - Database architecture
   - Best practices

2. **EXAMPLES.md** - More examples:
   - Advanced queries
   - Error scenarios
   - Python client code
   - Testing scenarios

3. **Code Files** - Read the source code:
   - `main.py` - See how routes are defined
   - `dependencies.py` - Understand dependency patterns
   - `middleware.py` - Learn middleware structure
   - `crud.py` - Study database operations

---

## 🐛 Troubleshooting

### Server won't start?
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Use a different port
uvicorn main:app --reload --port 8001
```

### Database errors?
```bash
# Delete the database and restart
rm fastapi_learning.db
uvicorn main:app --reload
```

### Import errors?
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Can't create a user?
- Check if email/username already exists
- Verify JSON format is correct
- Check server logs for error messages

---

## 🎯 Key Takeaways

After completing the quick start, you've learned:

✅ **Dependency Injection**
- Automatic database session management
- Query parameter validation
- API key authentication

✅ **Middleware**
- Request timing
- CORS headers
- Global request processing

✅ **Database Operations**
- CRUD operations
- SQLite with SQLAlchemy
- Automatic table creation

---

## 💡 Tips

- **Use `/docs`** - Interactive documentation is your best friend
- **Check logs** - The terminal shows middleware output and errors
- **Read code comments** - Every file has detailed explanations
- **Experiment** - Break things! That's how you learn
- **Start simple** - Master basics before adding complexity

---

## 🚀 Next Steps

1. ✅ Complete this quick start
2. 📖 Read TUTORIAL.md for deep understanding
3. 🧪 Try all examples from EXAMPLES.md
4. 💻 Modify the code and add features
5. 🎓 Build your own endpoints
6. 🏗️ Create a new model (e.g., Blog Posts)

---

## 🆘 Need Help?

- Check the documentation files in this project
- Visit FastAPI docs: https://fastapi.tiangolo.com/
- Read SQLAlchemy docs: https://docs.sqlalchemy.org/
- Try the interactive `/docs` endpoint

---

**You're all set! 🎉**

Start exploring the code and experimenting with the API. The best way to learn is by doing!
