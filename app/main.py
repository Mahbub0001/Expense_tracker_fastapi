from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import auth, transactions

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personal Expense Tracker API",
    description="Backend API for managing personal expenses and income with JWT authentication and PostgreSQL.",
    version="1.0.0",
)

# Enable CORS for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(transactions.router)


@app.get("/", tags=["Health Check"])
def root():
    return {
        "message": "Welcome to Personal Expense Tracker API",
        "docs": "/docs",
        "status": "active",
    }
