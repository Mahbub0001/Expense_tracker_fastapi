from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transaction, User
from app.schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)
from app.auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new transaction:
    - Automatically assigns the logged-in user as the transaction owner
    - Validates that amount is positive (>0) and type is 'income' or 'expense'
    - Saves and returns the created transaction
    """
    new_transaction = Transaction(
        title=transaction_data.title,
        amount=transaction_data.amount,
        type=transaction_data.type,
        category=transaction_data.category,
        date=transaction_data.date,
        owner_id=current_user.id,
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction


@router.get("/filter", response_model=List[TransactionResponse])
def filter_transactions(
    type: Optional[str] = Query(None, description="Filter by transaction type ('income' or 'expense')"),
    category: Optional[str] = Query(None, description="Filter by category"),
    minimum_amount: Optional[float] = Query(None, description="Filter by minimum amount"),
    maximum_amount: Optional[float] = Query(None, description="Filter by maximum amount"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Filter transactions belonging to the logged-in user:
    - Supports filtering by type, category, minimum_amount, and maximum_amount
    """
    query = db.query(Transaction).filter(Transaction.owner_id == current_user.id)

    if type:
        query = query.filter(Transaction.type == type)
    if category:
        query = query.filter(func.lower(Transaction.category) == category.lower())
    if minimum_amount is not None:
        query = query.filter(Transaction.amount >= minimum_amount)
    if maximum_amount is not None:
        query = query.filter(Transaction.amount <= maximum_amount)

    return query.all()


@router.get("", response_model=List[TransactionResponse])
@router.get("/", response_model=List[TransactionResponse], include_in_schema=False)
def get_all_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all transactions belonging to the logged-in user only.
    """
    transactions = (
        db.query(Transaction)
        .filter(Transaction.owner_id == current_user.id)
        .all()
    )
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction_by_id(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return a specific transaction:
    - Returns 404 if transaction doesn't exist or belongs to another user
    - Ensures user cannot access another user's transaction
    """
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.owner_id == current_user.id)
        .first()
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a transaction:
    - A user can update only their own transaction
    - Returns 404 if transaction is not found
    """
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.owner_id == current_user.id)
        .first()
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    update_dict = transaction_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_200_OK)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a transaction:
    - Deletes the matching row from the database
    - Returns 200 with confirmation message if found
    - Returns 404 if not found
    """
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.owner_id == current_user.id)
        .first()
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    db.delete(transaction)
    db.commit()
    return {"message": "Transaction deleted successfully"}
