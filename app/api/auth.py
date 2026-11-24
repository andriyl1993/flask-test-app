from flask import request, jsonify
from functools import wraps


def token_validation(func):
    @wraps(func)
    def inner(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Missing Authorization header"}), 401

        return func(*args, **kwargs)
    return inner
