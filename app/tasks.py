from flask import current_app
from app.containers import get_payment_service
from app.models.payment import PaymentStatus
from app.services.payment_provider import PaymentProvider, MockPaymentStatus
from app.logger import log


def fetch_payment_result(payment_id: int):
    payment = get_payment_service().get(payment_id)
    
    if not payment or payment.status != PaymentStatus.PENDING:
        log("Invalid payment_id or payment not pending")
        return

    payment_provider = PaymentProvider(url=current_app.config["PAYMENT_PROVIDER_URL"])
    for _ in range(5):  # Poll for a maximum of 5 times
        result = payment_provider.poll_result(payment.transaction_id)
        if result.status == MockPaymentStatus.SUCCESS:
            get_payment_service().update_status(payment.id, PaymentStatus.SUCCESS)
            log(f"Payment successful for payment_id: {payment.id}")
        elif result.status == MockPaymentStatus.ERROR:
            get_payment_service().update_status(payment.id, PaymentStatus.FAILED)
            log(f"Payment failed for payment_id: {payment.id}")

        if result.status != MockPaymentStatus.PENDING:
            break
