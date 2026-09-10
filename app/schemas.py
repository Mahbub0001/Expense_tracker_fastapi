from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# --- User Schemas ---

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=4)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


# --- Token Schemas ---

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# --- Transaction Schemas ---

class TransactionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    amount: float = Field(..., gt=0, description="Amount must be a positive number")
    type: Literal["income", "expense"] = Field(..., description="Type must be either 'income' or 'expense'")
    category: str = Field(..., min_length=1, max_length=100)
    date: date


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    amount: Optional[float] = Field(None, gt=0, description="Amount must be a positive number")
    type: Optional[Literal["income", "expense"]] = Field(None, description="Type must be either 'income' or 'expense'")
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    date: Optional[date] = None


class TransactionResponse(TransactionBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
