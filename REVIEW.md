# FastAPI Quick Review

Everything you learned in this session, in one place.

---

## 1. Pydantic Schemas

Two schemas, two jobs — one for what comes **in**, one for what goes **out**.

```python
# schemas.py

class UserCreate(BaseModel):       # INCOMING — what the client sends
    email: EmailStr                # must be valid email format
    username: str                  # required string
    full_name: Optional[str] = None  # optional

class UserResponse(BaseModel):     # OUTGOING — what you send back
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
```

**How it works in a route:**
```python
@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, ...):
    #             ↑ incoming payload        ↑ outgoing filter
```

- `user: schemas.UserCreate` → FastAPI reads the JSON body, validates it, gives you a Python object
- `response_model=schemas.UserResponse` → whatever you return gets filtered through this before going to client
- Fields NOT in `UserResponse` are silently dropped — this is how you prevent leaking passwords etc.
- If validation fails (bad email, missing field) → FastAPI returns 422 automatically, your code never runs

**model_dump()** — converts Pydantic object back to a plain dict:
```python
user.model_dump()
# {"email": "alice@example.com", "username": "alice", "full_name": "Alice Wonder"}

user_update.model_dump(exclude_unset=True)
# only fields the client actually sent — used in PATCH to avoid overwriting fields with None
```

---

## 2. Dependency Injection

FastAPI calls helper functions for you and passes the result into your route. You declare what you need, FastAPI provides it.

### Database connection dependency
```python
# database.py
def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn      # FastAPI injects this into your route
    finally:
        conn.close()    # always runs, even if an error occurs
```

```python
# used in route
@app.get("/users/")
def list_users(conn: sqlite3.Connection = Depends(get_db)):
    #                                      ↑ FastAPI calls get_db() and passes the result here
    return crud.get_users(conn)
```

### Class-based dependency (pagination)
```python
# dependencies.py
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

```python
@app.get("/users/")
def list_users(commons: CommonQueryParams = Depends(), conn = Depends(get_db)):
    return crud.get_users(conn, skip=commons.skip, limit=commons.limit, search=commons.search)
```

### Auth dependency
```python
async def get_api_key(x_api_key: str = Header(None)):
    if x_api_key != "secret-key-123":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key

@app.get("/secure/users/")
def secure_endpoint(conn = Depends(get_db), api_key = Depends(get_api_key)):
    # only runs if API key is valid
    return crud.get_users(conn)
```

### How FastAPI figures out where to look
```python
def update_user(
    user_id: int,                           # primitive type matching {user_id} in URL → path param
    user_update: schemas.UserUpdate,        # Pydantic model → request body (JSON)
    conn = Depends(get_db)                  # Depends() → dependency injection
):
```

---

## 3. Route Patterns

```python
@app.get("/users/")           # list — no ID needed
@app.get("/users/{user_id}")  # get one — ID in URL
@app.post("/users/")          # create — body required
@app.patch("/users/{user_id}")# partial update — ID in URL + body
@app.delete("/users/{user_id}")# delete — ID in URL
```

**Calling from Python:**
```python
import requests

requests.get("http://localhost:8000/users/")
requests.get("http://localhost:8000/users/3")           # path param
requests.get("http://localhost:8000/users/?skip=0&limit=5")  # query params
requests.post("http://localhost:8000/users/", json={...})    # json= not body=
requests.patch("http://localhost:8000/users/3", json={"full_name": "New Name"})
requests.delete("http://localhost:8000/users/3")
```

**Status codes:**
```
200 → success (GET, PATCH)
201 → created (POST)
204 → deleted, no body returned (DELETE) — return value is ignored
404 → not found
400 → bad request (duplicate email etc.)
403 → forbidden (wrong API key)
422 → validation failed (Pydantic caught it)
```

---

## 4. Middleware

Runs on **every** request. Code before `call_next` runs before your route, code after runs before response goes to client.

```python
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start_time = time.time()              # ← before route

    response = await call_next(request)   # ← your route runs here

    process_time = time.time() - start_time  # ← after route
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"

    return response   # ← passes up to next middleware, eventually to client
```

**With multiple middlewares:**
- Client gets ONE response — middlewares chain, not run in parallel
- Last registered = first to run on the way in
- Each `return response` passes the baton up, not to the client

```
Request → logging_middleware → timing_middleware → CORS → your route
Response ← logging_middleware ← timing_middleware ← CORS ← your route
```

**CORS** — needed so browsers from other domains (frontend apps) can call your API:
```python
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
```

---

## 5. Async / Await

**The rule:** anything that waits for something outside your code → `async def` + `await` it.

```
Needs await:          database queries, HTTP calls to other APIs, reading files
Does NOT need await:  math, string formatting, converting dicts, pure Python logic
```

```python
# async because it awaits something
async def timing_middleware(request: Request, call_next):
    response = await call_next(request)  # pause here, other requests can run
    return response
```

**Why it matters:**
- Without async: 100 requests queue up, each waits for the one before
- With async: 100 requests run concurrently, each pauses at `await` and lets others progress

**Our sqlite3 limitation:**
```python
# sqlite3 is NOT async — this blocks even with async/await keywords
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

For true async you'd need `aiosqlite`:
```python
await cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
row = await cursor.fetchone()
```

The chain must be async all the way down:
```
async route → await crud function → await db driver → database
```
If any link is blocking, the whole thing blocks at that point.

---

## 6. Raw SQL Patterns

```python
# connection setup — row_factory lets you do row["email"] instead of row[0]
conn = sqlite3.connect("fastapi_learning.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# SELECT one
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
row = cursor.fetchone()
return dict(row) if row else None

# SELECT many with pagination
cursor.execute("SELECT * FROM users LIMIT ? OFFSET ?", (limit, skip))
rows = cursor.fetchall()
return [dict(row) for row in rows]   # row_to_dict only handles one row, so loop it

# SELECT with search
pattern = f"%{search}%"
cursor.execute("SELECT * FROM users WHERE username LIKE ? OR email LIKE ?", (pattern, pattern))

# INSERT
cursor.execute("INSERT INTO users (email, username, full_name) VALUES (?, ?, ?)", (email, username, full_name))
conn.commit()
user_id = cursor.lastrowid   # get the auto-generated ID

# UPDATE (dynamic — only update fields that were sent)
cursor.execute("UPDATE users SET full_name = ?, updated_at = ? WHERE id = ?", (full_name, now, user_id))
conn.commit()

# DELETE
cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
conn.commit()

# COUNT
cursor.execute("SELECT COUNT(*) as count FROM users")
count = cursor.fetchone()["count"]
```

**Never do this — SQL injection risk:**
```python
query = f"SELECT * FROM users WHERE id = {user_id}"  # ❌ dangerous
cursor.execute(query)
```

**Always use `?` placeholders:**
```python
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))  # ✅ safe
```

**fetchone vs fetchall vs fetchmany:**
- `execute()` sends the query, results stay on DB side
- `fetchone()` pulls 1 row into Python
- `fetchall()` pulls all rows — fine for small tables
- `fetchmany(100)` pulls N rows at a time — use for large tables to avoid memory issues

---

## 7. Starting the Server

```bash
uvicorn main:app --reload
```

- `main` → the filename `main.py`
- `app` → the FastAPI instance inside it
- `--reload` → auto-restarts when you change code

Interactive docs: **http://localhost:8000/docs**
