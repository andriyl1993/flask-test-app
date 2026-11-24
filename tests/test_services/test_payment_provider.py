import unittest
from unittest.mock import patch
from uuid import UUID

from app.services.payment_provider import (
    MockPaymentStatus,
    PaymentProvider,
)


class PaymentProviderTests(unittest.TestCase):
    def setUp(self):
        self.provider = PaymentProvider("http://provider.test")

    def test_pay_returns_a_transaction_id_and_pending_status(self):
        transaction_id = UUID("12345678-1234-5678-1234-567812345678")

        with patch(
            "app.services.payment_provider.uuid.uuid4",
            return_value=transaction_id,
        ):
            result = self.provider.pay(
                provider_token="token",
                amount=10.0,
                shop_account="account",
            )

        self.assertEqual(result.transaction_id, str(transaction_id))
        self.assertEqual(result.status, MockPaymentStatus.PENDING)

    def test_poll_result_preserves_transaction_id_and_maps_pending(self):
        with patch("app.services.payment_provider.random.randint", return_value=0):
            result = self.provider.poll_result("transaction-1")

        self.assertEqual(result.transaction_id, "transaction-1")
        self.assertEqual(result.status, MockPaymentStatus.PENDING)

    def test_poll_result_maps_success(self):
        with patch("app.services.payment_provider.random.randint", return_value=1):
            result = self.provider.poll_result("transaction-1")

        self.assertEqual(result.transaction_id, "transaction-1")
        self.assertEqual(result.status, MockPaymentStatus.SUCCESS)


if __name__ == "__main__":
    unittest.main()
