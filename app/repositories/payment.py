from app.models.payment import Payment
from app.dtos import CreatePaymentDTO, UpdatePaymentStatusDTO, UpdatePaymentTransactionIdDTO
from app.db_session import SessionLocal


class PaymentRepository:
    model = Payment
    
    def __init__(self, db=None):
        self._session_factory = db.session if db is not None else SessionLocal

    def create(self, payment: CreatePaymentDTO) -> Payment:
        with self._session_factory() as session:
            payment_instance = self.model(**payment.to_dict(exclude_none=True))
            session.add(payment_instance)
            session.commit()
            return payment_instance

    def get(self, payment_id: int) -> Payment | None:
        with self._session_factory() as session:
            return session.query(self.model).filter_by(id=payment_id).first()

    def update(self, payment: UpdatePaymentStatusDTO | UpdatePaymentTransactionIdDTO) -> None:
        with self._session_factory() as session:
            payment_instance = session.query(self.model).filter_by(id=payment.payment_id).first()
            if payment_instance:
                if isinstance(payment, UpdatePaymentStatusDTO):
                    payment_instance.status = payment.status
                elif isinstance(payment, UpdatePaymentTransactionIdDTO):
                    payment_instance.transaction_id = payment.transaction_id
                session.commit()
