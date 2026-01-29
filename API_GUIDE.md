# Running the Application

Your project has **two ways to access it**:

## Option 1: Streamlit UI (Recommended for Users)

```bash
streamlit run main.py
```

- Opens at **http://localhost:8501**
- Full web interface for managing transactions
- Login/Register built-in

## Option 2: FastAPI REST API (For Developers/Integration)

```bash
uvicorn api_server:app --reload
```

- Runs at **http://localhost:8000**
- Interactive API docs at **http://localhost:8000/docs**
- Perfect for mobile apps, integrations, or automated requests

---

## API Endpoints (CRUD Operations)

### Authentication

**Register:**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "pass123"}'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "pass123"}'
```

Response includes your `user.id` (needed for other endpoints).

---

### Transactions (CRUD)

**Create (POST):**
```bash
curl -X POST "http://localhost:8000/transactions?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "date_iso": "2026-01-29",
    "amount": 50.00,
    "category": "Groceries",
    "ttype": "expense",
    "description": "Weekly shopping"
  }'
```

**Read (GET):**
```bash
curl "http://localhost:8000/transactions?user_id=1"
```

**Update (PUT):**
```bash
curl -X PUT "http://localhost:8000/transactions/1?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "date_iso": "2026-01-29",
    "amount": 75.00,
    "category": "Groceries",
    "ttype": "expense",
    "description": "Updated amount"
  }'
```

**Delete (DELETE):**
```bash
curl -X DELETE "http://localhost:8000/transactions/1?user_id=1"
```

---

### Monthly Summary

```bash
curl "http://localhost:8000/monthly-summary?user_id=1"
```

---

## Running Both Servers Simultaneously

Open **two terminals**:

**Terminal 1:** Streamlit UI
```bash
streamlit run main.py
```

**Terminal 2:** FastAPI server
```bash
uvicorn api_server:app --reload
```

Now you have:
- UI at **http://localhost:8501** for manual use
- API at **http://localhost:8000** for programmatic access
- API docs at **http://localhost:8000/docs** (Swagger UI)
