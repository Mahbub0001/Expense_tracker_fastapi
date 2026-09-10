# Personal Expense Tracker API

A production-ready RESTful backend API built with **FastAPI**, **SQLAlchemy ORM**, **PostgreSQL**, and **JWT Authentication** to help users track personal income and expenses. Developed according to the **Phitron AI-ML Module 24 — Mid Term** requirements.

---

## Features

- **JWT Authentication & Authorization**:
  - Secure user registration and login with password hashing (`bcrypt`).
  - Bearer token generation with expiry for protected routes.
  - User isolation: users can only view, update, or delete their own transactions.
- **Database Models & Relationships**:
  - `User` table (one-to-many relationship with `Transaction`).
  - `Transaction` table with foreign key (`owner_id`) and cascade rules.
- **Transaction CRUD Operations**:
  - `POST /transactions`: Automatically sets logged-in user as owner, validates `amount > 0` and `type in ['income', 'expense']`.
  - `GET /transactions`: Retrieves all transactions belonging to the authenticated user.
  - `GET /transactions/{transaction_id}`: Retrieves specific transaction (returns 404 if not found or unauthorized).
  - `PUT /transactions/{transaction_id}`: Updates existing transaction for authenticated user (returns 404 if not found).
  - `DELETE /transactions/{transaction_id}`: Deletes transaction and returns a confirmation message (returns 404 if not found).
- **Transaction Filtering**:
  - `GET /transactions/filter`: Filter user's transactions by query parameters:
    - `type` (e.g. `expense` or `income`)
    - `category` (e.g. `Food`)
    - `minimum_amount` (e.g. `100`)
    - `maximum_amount` (e.g. `5000`)
- **Pytest Automated Tests**:
  - 100% passing test suite covering all 5 required test cases and filtering.

---

## Project Structure

```text
.
├── app/
│   ├── __init__.py
│   ├── auth.py             # Password hashing, JWT token handling & auth dependencies
│   ├── database.py         # SQLAlchemy engine, session maker, get_db dependency
│   ├── main.py             # FastAPI app initialization, middleware, routes
│   ├── models.py           # SQLAlchemy User and Transaction ORM models
│   ├── schemas.py          # Pydantic validation schemas
│   └── routers/
│       ├── __init__.py
│       ├── auth.py         # /auth/register and /auth/login endpoints
│       └── transactions.py # /transactions CRUD & /transactions/filter endpoints
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures, test database setup, TestClient
│   └── test_transactions.py# 5 required test cases + filter test
├── .env.example            # Sample environment variables
├── .gitignore              # Ignored files & directories
├── render.yaml             # Render deployment configuration
├── requirements.txt        # Pinned project dependencies
└── README.md               # Project documentation
```

---

## Database Schema

### User Model (`users`)
| Field | Type | Description |
|---|---|---|
| `id` | Integer | Primary key, indexed |
| `username` | String | Unique username, indexed |
| `email` | String | Unique email, indexed |
| `hashed_password` | String | Encrypted password |

### Transaction Model (`transactions`)
| Field | Type | Description |
|---|---|---|
| `id` | Integer | Primary key, indexed |
| `title` | String | Transaction title |
| `amount` | Float | Transaction amount (must be positive) |
| `type` | String | `"income"` or `"expense"` |
| `category` | String | Transaction category |
| `date` | Date | Transaction date |
| `owner_id` | Integer | Foreign key referencing `users.id` |

---

## Local Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/Mahbub0001/Expense_tracker_fastapi.git
cd Expense_tracker_fastapi
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup environment variables
Create a `.env` file in the root directory (refer to `.env.example`):
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/expense_tracker_db
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
*(Note: If `DATABASE_URL` is omitted, the application will automatically default to SQLite for local development).*

### 5. Run the application
```bash
uvicorn app.main:app --reload
```
The API will be available at:
- **API Root**: `http://127.0.0.1:8000/`
- **Interactive OpenAPI Documentation (Swagger UI)**: `http://127.0.0.1:8000/docs`
- **Alternative Documentation (ReDoc)**: `http://127.0.0.1:8000/redoc`

---

## Running Automated Tests

Run the test suite with `pytest`:
```bash
pytest tests/ -v
```

All 6 test cases (including the 5 required core functionality tests) will execute against an isolated SQLite test database:
- `test_create_transaction`: Validates positive amount, type validation, user assignment.
- `test_get_all_transactions`: Validates user-only transaction retrieval.
- `test_get_specific_transaction`: Validates retrieval by ID and 404 behavior.
- `test_update_transaction`: Validates updating own transaction and 404 on missing/unauthorized.
- `test_delete_transaction`: Validates successful 200 deletion message and 404 for missing.
- `test_filter_transactions`: Validates filtering by type, category, and amount range.

---

## API Endpoints Summary

### Authentication
| Method | Endpoint | Description | Request Body | Auth Required |
|---|---|---|---|---|
| `POST` | `/auth/register` | Register a new user | `{"username": "...", "email": "...", "password": "..."}` | No |
| `POST` | `/auth/login` | Authenticate & get JWT | `{"username": "...", "password": "..."}` | No |

### Transactions
| Method | Endpoint | Description | Query / Path Parameters | Auth Required |
|---|---|---|---|---|
| `POST` | `/transactions` | Create transaction | JSON body (`title`, `amount`, `type`, `category`, `date`) | Bearer Token |
| `GET` | `/transactions` | Get all transactions | None | Bearer Token |
| `GET` | `/transactions/filter` | Filter transactions | `type`, `category`, `minimum_amount`, `maximum_amount` | Bearer Token |
| `GET` | `/transactions/{id}` | Get transaction by ID | `id` (int) | Bearer Token |
| `PUT` | `/transactions/{id}` | Update transaction | `id` (int), JSON body | Bearer Token |
| `DELETE`| `/transactions/{id}` | Delete transaction | `id` (int) | Bearer Token |

---

## Deploying to Render with Online PostgreSQL

### Step 1: Create a PostgreSQL Database on Render
1. Log in to [Render](https://render.com).
2. Click **New +** -> **PostgreSQL**.
3. Name your database (e.g. `expense-tracker-db`).
4. Click **Create Database**.
5. Once provisioned, copy the **Internal Database URL** (or **External Database URL** if deploying outside Render's network).

### Step 2: Create a Web Service on Render
1. In Render Dashboard, click **New +** -> **Web Service**.
2. Connect your GitHub repository: `https://github.com/Mahbub0001/Expense_tracker_fastapi`.
3. Configure the settings:
   - **Name**: `expense-tracker-fastapi`
   - **Region**: Closest to you (e.g., Singapore, Frankfurt, Oregon)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Under **Environment Variables**, add:
   - `DATABASE_URL`: *(Paste your Render PostgreSQL connection string)*
   - `SECRET_KEY`: *(Provide a long random string)*
   - `ALGORITHM`: `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: `60`
5. Click **Create Web Service**.

Render will automatically build and deploy the application. Once live, open your Render URL (e.g. `https://expense-tracker-fastapi.onrender.com/docs`) to test the live API!
