# 📚 Raw SQL Guide

This project uses **raw SQL queries** instead of an ORM (like SQLAlchemy). This gives you direct control and understanding of the SQL being executed.

---

## 🎯 Why Raw SQL?

**Advantages:**
- ✅ **Direct Control**: You write exactly what you want to execute
- ✅ **Learning**: Great for understanding SQL fundamentals
- ✅ **Performance**: No ORM overhead
- ✅ **Debugging**: Easy to see exactly what queries run
- ✅ **Simplicity**: No need to learn ORM syntax

**When to use:**
- Learning SQL
- Simple applications
- Performance-critical queries
- Full control over queries

---

## 🗄️ Database Setup

### Table Structure

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    full_name TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
)
```

### Indexes for Performance

```sql
-- Speed up queries by email
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)

-- Speed up queries by username
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)
```

---

## 📖 CRUD Operations Explained

### 1. CREATE (INSERT)

**Code (`crud.py`):**
```python
def create_user(conn: sqlite3.Connection, user_data: Dict[str, Any]):
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO users (email, username, full_name)
        VALUES (?, ?, ?)
        """,
        (user_data["email"], user_data["username"], user_data.get("full_name"))
    )
    
    conn.commit()
    user_id = cursor.lastrowid
    return get_user(conn, user_id)
```

**SQL Executed:**
```sql
INSERT INTO users (email, username, full_name)
VALUES ('alice@example.com', 'alice', 'Alice Wonder')
```

**Key Concepts:**
- `?` are placeholders (prevents SQL injection)
- `cursor.lastrowid` gets the auto-generated ID
- `conn.commit()` saves the changes
- We fetch the complete record after inserting

---

### 2. READ (SELECT)

#### Get Single User

**Code:**
```python
def get_user(conn: sqlite3.Connection, user_id: int):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    return dict(row) if row else None
```

**SQL Executed:**
```sql
SELECT * FROM users WHERE id = 1
```

#### Get Multiple Users with Pagination

**Code:**
```python
def get_users(conn: sqlite3.Connection, skip: int = 0, limit: int = 10):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users LIMIT ? OFFSET ?",
        (limit, skip)
    )
    rows = cursor.fetchall()
    return [dict(row) for row in rows]
```

**SQL Executed:**
```sql
-- Get first 10 users
SELECT * FROM users LIMIT 10 OFFSET 0

-- Get next 10 users (page 2)
SELECT * FROM users LIMIT 10 OFFSET 10
```

#### Search with LIKE

**Code:**
```python
def get_users(conn, search="alice"):
    cursor = conn.cursor()
    search_pattern = f"%{search}%"
    cursor.execute(
        """
        SELECT * FROM users 
        WHERE username LIKE ? OR email LIKE ? OR full_name LIKE ?
        LIMIT ? OFFSET ?
        """,
        (search_pattern, search_pattern, search_pattern, limit, skip)
    )
    return [dict(row) for row in cursor.fetchall()]
```

**SQL Executed:**
```sql
SELECT * FROM users 
WHERE username LIKE '%alice%' 
   OR email LIKE '%alice%' 
   OR full_name LIKE '%alice%'
LIMIT 10 OFFSET 0
```

**LIKE Patterns:**
- `%alice%` - Contains "alice" anywhere
- `alice%` - Starts with "alice"
- `%alice` - Ends with "alice"

---

### 3. UPDATE

**Code:**
```python
def update_user(conn: sqlite3.Connection, user_id: int, update_data: Dict):
    # Build dynamic UPDATE query
    update_fields = []
    update_values = []
    
    for field, value in update_data.items():
        if value is not None:
            update_fields.append(f"{field} = ?")
            update_values.append(value)
    
    update_fields.append("updated_at = ?")
    update_values.append(datetime.utcnow().isoformat())
    update_values.append(user_id)
    
    query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
    
    cursor = conn.cursor()
    cursor.execute(query, update_values)
    conn.commit()
```

**SQL Executed (updating full_name):**
```sql
UPDATE users 
SET full_name = 'Alice in Wonderland', updated_at = '2026-10-04T10:30:00'
WHERE id = 1
```

**SQL Executed (updating multiple fields):**
```sql
UPDATE users 
SET full_name = 'Bob Builder', is_active = 0, updated_at = '2026-10-04T10:30:00'
WHERE id = 2
```

**Why Dynamic Query?**
- Only update fields that are provided
- Partial updates (PATCH pattern)
- Flexible and efficient

---

### 4. DELETE

**Code:**
```python
def delete_user(conn: sqlite3.Connection, user_id: int):
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
```

**SQL Executed:**
```sql
DELETE FROM users WHERE id = 3
```

---

## 🔒 SQL Injection Prevention

### ❌ NEVER DO THIS (Vulnerable):
```python
# DON'T USE STRING FORMATTING!
user_id = request.get("id")
query = f"SELECT * FROM users WHERE id = {user_id}"  # DANGEROUS!
cursor.execute(query)
```

**Why dangerous?**
If `user_id = "1 OR 1=1"`, the query becomes:
```sql
SELECT * FROM users WHERE id = 1 OR 1=1
```
This returns ALL users!

### ✅ ALWAYS DO THIS (Safe):
```python
# USE PARAMETERIZED QUERIES
user_id = request.get("id")
cursor.execute(
    "SELECT * FROM users WHERE id = ?",
    (user_id,)  # Tuple of parameters
)
```

**Parameters are:**
- Automatically escaped
- Type-safe
- SQL injection proof

---

## 🎨 Working with Results

### sqlite3.Row

We configure the connection to return `sqlite3.Row` objects:

```python
conn = sqlite3.connect(DATABASE_URL)
conn.row_factory = sqlite3.Row  # This is the magic!
```

**Benefits:**
- Access columns by name: `row['email']`
- Convert to dict: `dict(row)`
- Still access by index: `row[0]`

### Examples

```python
# Fetch one result
cursor.execute("SELECT * FROM users WHERE id = ?", (1,))
row = cursor.fetchone()
print(row['email'])  # 'alice@example.com'
print(dict(row))     # {'id': 1, 'email': 'alice@example.com', ...}

# Fetch multiple results
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
for row in rows:
    print(f"{row['username']}: {row['email']}")

# Convert all to list of dicts
users = [dict(row) for row in rows]
```

---

## 🛠️ Common SQL Patterns

### Count Records

```python
cursor.execute("SELECT COUNT(*) as count FROM users")
result = cursor.fetchone()
count = result['count']
```

```sql
SELECT COUNT(*) as count FROM users
```

### Check if Exists

```python
cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
exists = cursor.fetchone() is not None
```

```sql
SELECT 1 FROM users WHERE email = 'test@example.com'
```

### Order Results

```python
cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
```

```sql
SELECT * FROM users ORDER BY created_at DESC
```

### Filter Active Users

```python
cursor.execute("SELECT * FROM users WHERE is_active = 1")
```

```sql
SELECT * FROM users WHERE is_active = 1
```

### Multiple Conditions

```python
cursor.execute(
    """
    SELECT * FROM users 
    WHERE is_active = 1 AND created_at > ?
    ORDER BY created_at DESC
    """,
    (start_date,)
)
```

---

## 💾 Connection Management

### Current Pattern (with Dependency Injection)

```python
def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
```

**FastAPI automatically:**
- Creates connection when endpoint is called
- Passes it to your function
- Closes it after response is sent

### Manual Connection (for scripts)

```python
def manual_query():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        return [dict(row) for row in users]
    finally:
        conn.close()
```

---

## 🧪 Testing SQL Queries

### Using SQLite CLI

```bash
# Open database
sqlite3 fastapi_learning.db

# View all tables
.tables

# View table structure
.schema users

# Run queries
SELECT * FROM users;
SELECT * FROM users WHERE username LIKE '%alice%';
SELECT COUNT(*) FROM users;

# Exit
.exit
```

### Using Python Script

```python
import sqlite3

conn = sqlite3.connect('fastapi_learning.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Test query
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

for user in users:
    print(dict(user))

conn.close()
```

---

## 🎓 SQL Cheat Sheet

### SELECT Variations

```sql
-- All columns
SELECT * FROM users

-- Specific columns
SELECT id, username, email FROM users

-- With condition
SELECT * FROM users WHERE id = 1

-- Multiple conditions
SELECT * FROM users WHERE is_active = 1 AND email LIKE '%@example.com'

-- Ordering
SELECT * FROM users ORDER BY created_at DESC

-- Limit
SELECT * FROM users LIMIT 10

-- Pagination
SELECT * FROM users LIMIT 10 OFFSET 20

-- Count
SELECT COUNT(*) as count FROM users

-- Distinct
SELECT DISTINCT email FROM users
```

### INSERT

```sql
-- Single row
INSERT INTO users (email, username, full_name)
VALUES ('test@example.com', 'test', 'Test User')

-- Multiple rows
INSERT INTO users (email, username) VALUES
  ('user1@example.com', 'user1'),
  ('user2@example.com', 'user2'),
  ('user3@example.com', 'user3')
```

### UPDATE

```sql
-- Update one field
UPDATE users SET full_name = 'New Name' WHERE id = 1

-- Update multiple fields
UPDATE users 
SET full_name = 'New Name', is_active = 0 
WHERE id = 1

-- Update all rows (be careful!)
UPDATE users SET is_active = 1

-- Conditional update
UPDATE users SET is_active = 0 WHERE created_at < '2026-01-01'
```

### DELETE

```sql
-- Delete one row
DELETE FROM users WHERE id = 1

-- Delete multiple rows
DELETE FROM users WHERE is_active = 0

-- Delete all (be careful!)
DELETE FROM users
```

---

## 🔍 Debugging Tips

### Print Queries

```python
query = "SELECT * FROM users WHERE id = ?"
params = (user_id,)
print(f"Executing: {query}")
print(f"Parameters: {params}")
cursor.execute(query, params)
```

### Check Row Count

```python
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
print(f"Found {len(rows)} users")
```

### View Query Results

```python
cursor.execute("SELECT * FROM users LIMIT 1")
row = cursor.fetchone()
print("Column names:", row.keys())
print("Values:", dict(row))
```

---

## 💡 Best Practices

1. **Always use parameterized queries** (`?` placeholders)
2. **Close connections** (or use dependency injection)
3. **Commit after writes** (`conn.commit()`)
4. **Use transactions** for multiple related operations
5. **Create indexes** for frequently queried columns
6. **Handle errors** with try/except
7. **Validate input** before queries
8. **Use LIMIT** for large result sets

---

## 🚀 Next Steps

1. Try writing your own SQL queries
2. Add new fields to the users table
3. Create a new table (e.g., posts)
4. Practice JOINs between tables
5. Learn about transactions
6. Explore SQLite-specific features

---

**Happy querying! 🎉**
