from dataclasses import dataclass
from app.utils import dataclass_to_dict


@dataclass
class CreatePaymentDTO:
    cart_id: int
    amount: float
    
    def to_dict(self, exclude_none: bool = False) -> dict:
        return dataclass_to_dict(self, exclude_none=exclude_none)


@dataclass
class UpdatePaymentStatusDTO:
    payment_id: int
    status: str
    
    def to_dict(self, exclude_none: bool = False) -> dict:
        return dataclass_to_dict(self, exclude_none=exclude_none)


@dataclass
class UpdatePaymentTransactionIdDTO:
    payment_id: int
    transaction_id: str

    def to_dict(self, exclude_none: bool = False) -> dict:
        return dataclass_to_dict(self, exclude_none=exclude_none)
