import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from sqlalchemy.exc import IntegrityError

from app.dtos import (
    CreatePaymentDTO,
    UpdatePaymentStatusDTO,
    UpdatePaymentTransactionIdDTO,
)
from app.exceptions import PaymentExistsException
from app.models.payment import PaymentStatus
from app.services.payment import PaymentService


class PaymentServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()
        self.service = PaymentService(self.repository)

    def test_create_returns_payment_from_repository(self):
        payment = SimpleNamespace(id=42)
        self.repository.create.return_value = payment

        result = self.service.create(cart_id=11, amount=15.25)

        self.assertIs(result, payment)
        self.repository.create.assert_called_once_with(
            CreatePaymentDTO(cart_id=11, amount=15.25)
        )

    def test_create_translates_integrity_error(self):
        integrity_error = IntegrityError("insert", {}, Exception("duplicate"))
        self.repository.create.side_effect = integrity_error

        with self.assertRaises(PaymentExistsException) as raised:
            self.service.create(cart_id=11, amount=15.25)

        self.assertIs(raised.exception.__cause__, integrity_error)

    def test_get_delegates_to_repository(self):
        payment = SimpleNamespace(id=42)
        self.repository.get.return_value = payment

        result = self.service.get(42)

        self.assertIs(result, payment)
        self.repository.get.assert_called_once_with(42)

    def test_update_status_sends_status_dto_to_repository(self):
        self.service.update_status(42, PaymentStatus.SUCCESS)

        self.repository.update.assert_called_once_with(
            UpdatePaymentStatusDTO(
                payment_id=42,
                status=PaymentStatus.SUCCESS,
            )
        )

    def test_update_transaction_id_sends_transaction_dto_to_repository(self):
        self.service.update_transaction_id(42, "transaction-42")

        self.repository.update.assert_called_once_with(
            UpdatePaymentTransactionIdDTO(
                payment_id=42,
                transaction_id="transaction-42",
            )
        )


if __name__ == "__main__":
    unittest.main()
