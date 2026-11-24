from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PaymentCreateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    cart_id: int = Field(gt=0)
    provider_token: str = Field(min_length=1, max_length=512)
