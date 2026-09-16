from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.security import require_api_key
from app import models, schemas

router = APIRouter(prefix="/api/customers", tags=["Customers"])

@router.post("", response_model=schemas.CustomerOut, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: schemas.CustomerCreate, 
    db: Session = Depends(get_db),
    _api_key: str = Depends(require_api_key)
):
    db_customer = models.Customer(customer_ref=customer.customer_ref, name=customer.name)
    db.add(db_customer)
    try:
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer reference identity already exists"
        )

@router.get("/{id}/payments", response_model=list)
async def get_customer_payments(id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return db.query(models.Transaction).filter(models.Transaction.customer_id == id).all()
