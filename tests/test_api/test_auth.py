import unittest

from flask import Flask, jsonify

from app.api.auth import token_validation


class TokenValidationTests(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)

        @app.get("/protected")
        @token_validation
        def protected():
            return jsonify({"ok": True})

        self.client = app.test_client()

    def test_missing_authorization_header_is_rejected(self):
        response = self.client.get("/protected")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.get_json(),
            {"error": "Missing Authorization header"},
        )

    def test_authorization_header_allows_request(self):
        response = self.client.get(
            "/protected",
            headers={"Authorization": "test-token"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"ok": True})


if __name__ == "__main__":
    unittest.main()
