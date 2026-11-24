import uuid
import random
from dataclasses import dataclass


@dataclass
class MockPaymentDetails:
    transaction_id: str
    status: str


class MockPaymentStatus:
    SUCCESS = "success"
    PENDING = "pending"
    ERROR = "error"


class PaymentProvider:
    def __init__(self, url: str):
        self.url = url

    def pay(self, provider_token: str, amount: float, shop_account: str) -> MockPaymentDetails:
        # Here you would implement the logic to interact with the payment provider's API
        # For example, sending a request to the payment provider's endpoint with the cart_id and amount
        return MockPaymentDetails(transaction_id=str(uuid.uuid4()), status="pending")

    def poll_result(self, transaction_id: str) -> MockPaymentDetails:
        # Here you would implement the logic to poll the payment provider's API for the result of a payment
        # For example, sending a request to the payment provider's endpoint with the transaction_id
        response = random.randint(0, 4) % 4 == 0
        status = MockPaymentStatus.SUCCESS 
        if response == 1:
            status = MockPaymentStatus.PENDING
        elif response == 2:
            status = MockPaymentStatus.ERROR
            
        return MockPaymentDetails(transaction_id=transaction_id, status=status)
