import unittest

from app import create_app
from app.database import db


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {}
    PAYMENT_PROVIDER_URL = "http://provider.test"
    SHOP_ACCOUNT = "test-account"


class CreateAppTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def test_root_returns_healthy_status(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_app_uses_config_and_registers_database(self):
        self.assertTrue(self.app.config["TESTING"])
        self.assertEqual(self.app.config["SQLALCHEMY_DATABASE_URI"], "sqlite://")
        self.assertIs(self.app.extensions["sqlalchemy"], db)

    def test_api_blueprint_is_registered_under_api_prefix(self):
        paths = {rule.rule for rule in self.app.url_map.iter_rules()}

        self.assertIn("/api/payments/pay", paths)
        self.assertIn("/api/payments/<int:payment_id>", paths)


if __name__ == "__main__":
    unittest.main()
