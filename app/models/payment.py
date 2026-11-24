from app.database import db
from enum import StrEnum
from datetime import datetime, timezone
from sqlalchemy import Enum as SQLAlchemyEnum


class PaymentStatus(StrEnum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(
        db.Integer,
        nullable=False,
        unique=True,  # I assume each cart can have only one payment associated with it
    )
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(
        SQLAlchemyEnum(
            PaymentStatus,
            name="payment_status",
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum]
        ),
        nullable=False,
        default=PaymentStatus.PENDING
    )
    payment_method = db.Column(
        db.String(30),
        nullable=False,
        default="MOCK"
    )
    transaction_id = db.Column(db.String(100), unique=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
