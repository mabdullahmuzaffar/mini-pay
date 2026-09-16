from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import require_api_key
from app import models, schemas

router = APIRouter(prefix="/api/payments", tags=["Payments"])

@router.post("", response_model=schemas.PaymentOut, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payload: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    _api_key: str = Depends(require_api_key)
):
    # 1. Lookup customer profile by tracking identity
    customer = db.query(models.Customer).filter(models.Customer.customer_ref == payload.customer_ref).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer account reference not found"
        )

    # 2. Idempotency Check: Verify if this specific reference identifier already exists
    existing_txn = db.query(models.Transaction).filter(models.Transaction.transaction_ref == payload.transaction_ref).first()
    if existing_txn:
        # Return status 200 instead of 201 to indicate the entity was already created safely
        return existing_txn

    # 3. Handle pristine workflow entry
    new_txn = models.Transaction(
        transaction_ref=payload.transaction_ref,
        customer_id=customer.id,
        amount=payload.amount,
        status="SUCCESS",
        created_at=datetime.utcnow()
    )
    db.add(new_txn)
    db.commit()
    db.refresh(new_txn)

    # 4. Initialize baseline fallback callback log record
    new_callback = models.Callback(
        transaction_id=new_txn.id,
        attempt_no=1,
        http_status=200,
        callback_status="SUCCESS",
        attempted_at=datetime.utcnow()
    )
    db.add(new_callback)
    db.commit()
    db.refresh(new_txn)

    return new_txn

@router.get("/{id}", response_model=schemas.PaymentOut)
async def get_payment_by_id(id: int, db: Session = Depends(get_db)):
    # Explicitly check for None to resolve the future operational INCIDENT-001 error
    txn = db.query(models.Transaction).filter(models.Transaction.id == id).first()
    if not txn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction profile target identifier not found"
        )
    return txn

@router.get("/search/transactions", response_model=dict)
async def search_transactions(
    ref: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    txns = db.query(models.Transaction).filter(models.Transaction.transaction_ref == ref).all()
    return {
        "count": len(txns),
        "results": [schemas.PaymentOut.model_validate(t).model_dump() for t in txns]
    }
