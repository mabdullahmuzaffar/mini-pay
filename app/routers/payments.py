from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import require_api_key
from app import models, schemas

router = APIRouter(tags=["Payments"])

@router.post("/api/payments", response_model=schemas.PaymentOut, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payload: schemas.PaymentCreate,
    response: Response,
    db: Session = Depends(get_db),
    _api_key: str = Depends(require_api_key)
):
    customer = db.query(models.Customer).filter(models.Customer.customer_ref == payload.customer_ref).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    existing_txn = db.query(models.Transaction).filter(models.Transaction.transaction_ref == payload.transaction_ref).first()
    if existing_txn:
        response.status_code = status.HTTP_200_OK
        return existing_txn

    new_txn = models.Transaction(
        transaction_ref=payload.transaction_ref,
        customer_id=customer.id,
        amount=payload.amount,
        status="SUCCESS",
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_txn)
    db.commit()
    db.refresh(new_txn)

    new_callback = models.Callback(
        transaction_id=new_txn.id,
        attempt_no=1,
        http_status=200,
        callback_status="SUCCESS",
        attempted_at=datetime.now(timezone.utc)
    )
    db.add(new_callback)
    db.commit()
    db.refresh(new_txn)
    return new_txn

@router.get("/api/payments/{id}", response_model=schemas.PaymentOut)
async def get_payment_by_id(id: int, db: Session = Depends(get_db)):
    txn = db.query(models.Transaction).filter(models.Transaction.id == id).first()
    # INTENTIONAL BUG FOR INCIDENT-001: Accessing attributes on None will trigger a 500 error payload
    return txn

@router.get("/api/transactions", response_model=dict)
async def search_transactions(
    ref: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    txns = db.query(models.Transaction).filter(models.Transaction.transaction_ref == ref).all()
    return {
        "count": len(txns),
        "results": [schemas.PaymentOut.model_validate(t).model_dump() for t in txns]
    }
