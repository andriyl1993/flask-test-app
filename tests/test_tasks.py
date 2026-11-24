import unittest
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

from app import create_app
from app.models.payment import PaymentStatus
from app.services.payment_provider import MockPaymentStatus
from app.tasks import fetch_payment_result


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {}
    PAYMENT_PROVIDER_URL = "http://provider.test"
    SHOP_ACCOUNT = "test-account"


class FetchPaymentResultTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_missing_payment_is_not_polled(self):
        service = Mock()
        service.get.return_value = None

        with (
            patch("app.tasks.get_payment_service", return_value=service),
            patch("app.tasks.PaymentProvider") as provider_class,
            patch("app.tasks.log"),
        ):
            fetch_payment_result(17)

        provider_class.assert_not_called()

    def test_non_pending_payment_is_not_polled(self):
        service = Mock()
        service.get.return_value = SimpleNamespace(status=PaymentStatus.SUCCESS)

        with (
            patch("app.tasks.get_payment_service", return_value=service),
            patch("app.tasks.PaymentProvider") as provider_class,
            patch("app.tasks.log"),
        ):
            fetch_payment_result(17)

        provider_class.assert_not_called()

    def test_successful_result_updates_payment_status(self):
        payment = SimpleNamespace(
            id=17,
            status=PaymentStatus.PENDING,
            transaction_id="transaction-17",
        )
        service = Mock()
        service.get.return_value = payment

        with (
            patch("app.tasks.get_payment_service", return_value=service),
            patch("app.tasks.PaymentProvider") as provider_class,
            patch("app.tasks.log"),
        ):
            provider_class.return_value.poll_result.return_value = SimpleNamespace(
                status=MockPaymentStatus.SUCCESS
            )
            fetch_payment_result(17)

        service.update_status.assert_called_once_with(17, PaymentStatus.SUCCESS)
        provider_class.return_value.poll_result.assert_called_once_with(
            "transaction-17"
        )

    def test_failed_result_maps_to_failed_payment_status(self):
        payment = SimpleNamespace(
            id=17,
            status=PaymentStatus.PENDING,
            transaction_id="transaction-17",
        )
        service = Mock()
        service.get.return_value = payment

        with (
            patch("app.tasks.get_payment_service", return_value=service),
            patch("app.tasks.PaymentProvider") as provider_class,
            patch("app.tasks.log"),
        ):
            provider_class.return_value.poll_result.return_value = SimpleNamespace(
                status=MockPaymentStatus.ERROR
            )
            fetch_payment_result(17)

        service.update_status.assert_called_once_with(17, PaymentStatus.FAILED)

    def test_pending_result_is_polled_at_most_five_times(self):
        payment = SimpleNamespace(
            id=17,
            status=PaymentStatus.PENDING,
            transaction_id="transaction-17",
        )
        service = Mock()
        service.get.return_value = payment

        with (
            patch("app.tasks.get_payment_service", return_value=service),
            patch("app.tasks.PaymentProvider") as provider_class,
            patch("app.tasks.log"),
        ):
            provider_class.return_value.poll_result.return_value = SimpleNamespace(
                status=MockPaymentStatus.PENDING
            )
            fetch_payment_result(17)

        self.assertEqual(
            provider_class.return_value.poll_result.call_args_list,
            [call("transaction-17")] * 5,
        )
        service.update_status.assert_not_called()


if __name__ == "__main__":
    unittest.main()
