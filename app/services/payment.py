from app.models.payment import Payment
from app.dtos import CreatePaymentDTO
from app.repositories.payment import PaymentRepository
from app.dtos import CreatePaymentDTO, UpdatePaymentStatusDTO, UpdatePaymentTransactionIdDTO
from sqlalchemy.exc import IntegrityError
from app.exceptions import PaymentExistsException


class PaymentService:
    model = Payment
    
    def __init__(self, repository: PaymentRepository):
        self._repository = repository

    def create(self, cart_id: int, amount: float) -> Payment:
        payment_dto = CreatePaymentDTO(cart_id=cart_id, amount=amount)
        try:
            return self._repository.create(payment_dto)
        except IntegrityError as e:
            raise PaymentExistsException from e

    def get(self, payment_id: int) -> Payment:
        return self._repository.get(payment_id)

    def update_status(self, payment_id: int, status: str) -> None:
        self._repository.update(UpdatePaymentStatusDTO(payment_id=payment_id, status=status))
    
    def update_transaction_id(self, payment_id: int, transaction_id: str) -> None:
        self._repository.update(UpdatePaymentTransactionIdDTO(payment_id=payment_id, transaction_id=transaction_id))
