from sqlalchemy import BigInteger, Integer, String, Numeric, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    customer_ref = mapped_column(String(40), nullable=False, unique=True)
    name = mapped_column(String(120), nullable=False)
    created_at = mapped_column(DateTime, nullable=False, server_default=func.now())

    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    transaction_ref = mapped_column(String(50), nullable=False)
    customer_id = mapped_column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("customers.id"), nullable=False)
    amount = mapped_column(Numeric(14, 2), nullable=False)
    status = mapped_column(String(20), nullable=False)
    created_at = mapped_column(DateTime, nullable=False)
    completed_at = mapped_column(DateTime, nullable=True)
    failure_code = mapped_column(String(40), nullable=True)

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_amount_positive"),
        CheckConstraint("status IN ('PROCESSING', 'SUCCESS', 'FAILED')", name="check_transaction_status"),
    )

    customer = relationship("Customer", back_populates="transactions")
    callbacks = relationship("Callback", back_populates="transaction", cascade="all, delete-orphan")


class Callback(Base):
    __tablename__ = "callbacks"

    id = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    transaction_id = mapped_column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("transactions.id"), nullable=False)
    attempt_no = mapped_column(Integer, nullable=False)
    http_status = mapped_column(Integer, nullable=True)
    callback_status = mapped_column(String(20), nullable=False)
    attempted_at = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("transaction_id", "attempt_no", name="uq_transaction_attempt"),
        CheckConstraint("callback_status IN ('SUCCESS', 'FAILED')", name="check_callback_status"),
    )

    transaction = relationship("Transaction", back_populates="callbacks")
