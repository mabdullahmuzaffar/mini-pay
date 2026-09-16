from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

class CustomerCreate(BaseModel):
    customer_ref: str = Field(..., max_length=40)
    name: str = Field(..., max_length=120)

class CustomerOut(BaseModel):
    id: int
    customer_ref: str
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CallbackOut(BaseModel):
    id: int
    transaction_id: int
    attempt_no: int
    http_status: Optional[int] = None
    callback_status: str
    attempted_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaymentCreate(BaseModel):
    customer_ref: str = Field(..., max_length=40)
    amount: Decimal = Field(..., gt=0)
    transaction_ref: str = Field(..., max_length=50)

class PaymentOut(BaseModel):
    id: int
    transaction_ref: str
    customer_id: int
    amount: Decimal
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    failure_code: Optional[str] = None
    callbacks: List[CallbackOut] = []

    model_config = ConfigDict(from_attributes=True)

class HealthOut(BaseModel):
    status: str
    database: str
    time: str

class ErrorOut(BaseModel):
    error: str
    detail: str
