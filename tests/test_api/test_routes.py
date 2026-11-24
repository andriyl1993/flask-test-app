import unittest
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app import create_app
from app.exceptions import PaymentExistsException
from app.models.payment import PaymentStatus


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {}
    PAYMENT_PROVIDER_URL = "http://provider.test"
    SHOP_ACCOUNT = "test-account"


class PaymentRoutesTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.auth_headers = {"Authorization": "test-token"}

    def test_invalid_payment_request_returns_validation_details(self):
        with patch("app.api.routes.get_payment_service") as get_service:
            response = self.client.post(
                "/api/payments/pay",
                json={"cart_id": 0, "amount": -1, "provider_token": ""},
                headers=self.auth_headers,
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Validation failed")
        get_service.assert_not_called()

    def test_duplicate_payment_returns_client_error(self):
        service = Mock()
        service.create.side_effect = PaymentExistsException

        with patch("app.api.routes.get_payment_service", return_value=service):
            response = self.client.post(
                "/api/payments/pay",
                json={
                    "cart_id": 1,
                    "amount": "10.00",
                    "provider_token": "provider-token",
                },
                headers=self.auth_headers,
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {"error": "Payment already exists for the given cart_id"},
        )

    def test_payment_creation_calls_provider_and_returns_transaction(self):
        payment = SimpleNamespace(id=23)
        service = Mock()
        service.create.return_value = payment
        provider_result = SimpleNamespace(transaction_id="transaction-1")

        with (
            patch("app.api.routes.get_payment_service", return_value=service),
            patch("app.api.routes.PaymentProvider") as provider_class,
            patch("app.api.routes.fetch_payment_result") as fetch_result,
        ):
            provider_class.return_value.pay.return_value = provider_result
            response = self.client.post(
                "/api/payments/pay",
                json={
                    "cart_id": 1,
                    "amount": "10.00",
                    "provider_token": "provider-token",
                },
                headers=self.auth_headers,
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "message": "Payment initiated",
                "transaction_id": "transaction-1",
                "payment_id": 23,
            },
        )
        service.create.assert_called_once_with(
            cart_id=1,
            amount=Decimal("10.00"),
        )
        service.update_transaction_id.assert_called_once_with(23, "transaction-1")
        fetch_result.assert_called_once_with(23)
        provider_class.return_value.pay.assert_called_once_with(
            provider_token="provider-token",
            amount=Decimal("10.00"),
            shop_account="test-account",
        )

    def test_provider_error_is_returned_as_server_error(self):
        service = Mock()
        service.create.return_value = SimpleNamespace(id=23)

        with (
            patch("app.api.routes.get_payment_service", return_value=service),
            patch("app.api.routes.PaymentProvider") as provider_class,
        ):
            provider_class.return_value.pay.side_effect = RuntimeError("provider down")
            response = self.client.post(
                "/api/payments/pay",
                json={
                    "cart_id": 1,
                    "amount": "10.00",
                    "provider_token": "provider-token",
                },
                headers=self.auth_headers,
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_json(),
            {
                "error": "Failed to initiate payment with the provider",
                "details": "provider down",
            },
        )

    def test_get_payment_returns_payment_fields(self):
        service = Mock()
        service.get.return_value = SimpleNamespace(
            id=23,
            cart_id=1,
            amount=Decimal("10.00"),
            status=PaymentStatus.PENDING,
            transaction_id="transaction-1",
        )

        with patch("app.api.routes.get_payment_service", return_value=service):
            response = self.client.get(
                "/api/payments/23",
                headers=self.auth_headers,
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "payment_id": 23,
                "cart_id": 1,
                "amount": "10.00",
                "status": "PENDING",
                "transaction_id": "transaction-1",
            },
        )
        service.get.assert_called_once_with(23)

    def test_get_payment_returns_not_found_when_missing(self):
        service = Mock()
        service.get.return_value = None

        with patch("app.api.routes.get_payment_service", return_value=service):
            response = self.client.get(
                "/api/payments/23",
                headers=self.auth_headers,
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.get_json(),
            {"error": "Payment not found"},
        )


if __name__ == "__main__":
    unittest.main()
