import unittest
from decimal import Decimal

from pydantic import ValidationError

from app.schemas import PaymentCreateSchema


class PaymentCreateSchemaTests(unittest.TestCase):
    def test_valid_payment_data_is_parsed(self):
        payment = PaymentCreateSchema.model_validate(
            {
                "cart_id": 7,
                "amount": "25.40",
                "provider_token": "provider-token",
            }
        )

        self.assertEqual(payment.cart_id, 7)
        self.assertEqual(payment.amount, Decimal("25.40"))
        self.assertEqual(payment.provider_token, "provider-token")

    def test_non_positive_amount_is_rejected(self):
        for amount in ("0", "-1.00"):
            with self.subTest(amount=amount):
                with self.assertRaises(ValidationError):
                    PaymentCreateSchema.model_validate(
                        {
                            "cart_id": 7,
                            "amount": amount,
                            "provider_token": "provider-token",
                        }
                    )

    def test_invalid_cart_id_and_provider_token_are_rejected(self):
        for data in (
            {
                "cart_id": 0,
                "amount": "1.00",
                "provider_token": "provider-token",
            },
            {"cart_id": 7, "amount": "1.00", "provider_token": ""},
        ):
            with self.subTest(data=data):
                with self.assertRaises(ValidationError):
                    PaymentCreateSchema.model_validate(data)

    def test_extra_fields_are_rejected(self):
        with self.assertRaises(ValidationError):
            PaymentCreateSchema.model_validate(
                {
                    "cart_id": 7,
                    "amount": "1.00",
                    "provider_token": "provider-token",
                    "unexpected": True,
                }
            )


if __name__ == "__main__":
    unittest.main()
