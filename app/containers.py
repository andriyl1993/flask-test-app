from app.database import db
from app.repositories.payment import PaymentRepository
from app.services.payment import PaymentService


def get_payment_service():
    payment_repository = PaymentRepository(db)
    return PaymentService(payment_repository)
