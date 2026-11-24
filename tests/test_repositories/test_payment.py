import unittest

from app import create_app
from app.database import db
from app.dtos import (
    CreatePaymentDTO,
    UpdatePaymentStatusDTO,
    UpdatePaymentTransactionIdDTO,
)
from app.models.payment import PaymentStatus
from app.repositories.payment import PaymentRepository


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {}


class PaymentRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.repository = PaymentRepository(db)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_and_get_payment(self):
        created = self.repository.create(
            CreatePaymentDTO(cart_id=100, amount=12.50)
        )

        payment = self.repository.get(created.id)

        self.assertIsNotNone(payment)
        self.assertEqual(payment.cart_id, 100)
        self.assertEqual(str(payment.amount), "12.50")
        self.assertEqual(payment.status, PaymentStatus.PENDING)

    def test_get_returns_none_when_payment_does_not_exist(self):
        self.assertIsNone(self.repository.get(999))

    def test_update_changes_payment_status(self):
        created = self.repository.create(
            CreatePaymentDTO(cart_id=101, amount=9.99)
        )

        self.repository.update(
            UpdatePaymentStatusDTO(
                payment_id=created.id,
                status=PaymentStatus.SUCCESS,
            )
        )

        payment = self.repository.get(created.id)
        self.assertEqual(payment.status, PaymentStatus.SUCCESS)

    def test_update_of_unknown_payment_is_a_no_op(self):
        self.repository.update(
            UpdatePaymentStatusDTO(
                payment_id=999,
                status=PaymentStatus.SUCCESS,
            )
        )

        self.assertIsNone(self.repository.get(999))

    def test_update_changes_payment_transaction_id(self):
        created = self.repository.create(
            CreatePaymentDTO(cart_id=102, amount=9.99)
        )

        self.repository.update(
            UpdatePaymentTransactionIdDTO(
                payment_id=created.id,
                transaction_id="transaction-102",
            )
        )

        payment = self.repository.get(created.id)
        self.assertEqual(payment.transaction_id, "transaction-102")


if __name__ == "__main__":
    unittest.main()
