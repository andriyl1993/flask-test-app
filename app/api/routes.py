from flask import Blueprint, current_app
from app.containers import get_payment_service
from app.schemas import PaymentCreateSchema
from flask import request, jsonify
from pydantic import ValidationError
from app.services.payment_provider import PaymentProvider
from app.api.auth import token_validation
from app.exceptions import PaymentExistsException
from app.tasks import fetch_payment_result


payment_bp = Blueprint("payments", __name__)


@payment_bp.post("pay")
@token_validation
def cart_pay():
    try:
        payment_data = PaymentCreateSchema.model_validate(request.get_json())
    except ValidationError as exc:
        return jsonify({
            "error": "Validation failed",
            "details": exc.errors(include_input=False)
        }), 400

    payment_service = get_payment_service()
    try:
        payment = payment_service.create(
            cart_id=payment_data.cart_id, 
            amount=payment_data.amount, 
        )
    except PaymentExistsException as e:
        return jsonify({"error": "Payment already exists for the given cart_id"}), 400

    payment_provider = PaymentProvider(url=current_app.config["PAYMENT_PROVIDER_URL"])
    try:
        payment_provider_instance = payment_provider.pay(
            provider_token=payment_data.provider_token,
            amount=payment_data.amount,
            shop_account=current_app.config["SHOP_ACCOUNT"],
        )
        payment_service.update_transaction_id(payment.id, payment_provider_instance.transaction_id)
    except Exception as e:
        # TODO: add retry logic if it needs
        return jsonify({"error": "Failed to initiate payment with the provider", "details": str(e)}), 500

    # poll results using celery or some job runner
    fetch_payment_result(payment.id)

    return jsonify({
        "message": "Payment initiated", 
        "transaction_id": payment_provider_instance.transaction_id,
        "payment_id": payment.id,
    }), 200


@payment_bp.get("/<int:payment_id>")
@token_validation
def get_payment_result(payment_id: int):
    payment = get_payment_service().get(payment_id)
    if not payment:
        return jsonify({"error": "Payment not found"}), 404

    return jsonify({
        "payment_id": payment.id,
        "cart_id": payment.cart_id,
        "amount": payment.amount,
        "status": payment.status.value,
        "transaction_id": payment.transaction_id,
    }), 200
