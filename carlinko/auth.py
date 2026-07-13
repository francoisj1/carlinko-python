"""
carlinko/auth.py

Authentication layer for the CarLinko API.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any

import httpx


DEFAULT_REGION = "ZA"

# Reuse the signing key recovered from the dashboard.
SIGN_KEY = "mYj3fzMpn77bir66"

USER_AGENT = "CarLinko/1.0"


class AuthenticationError(Exception):
    """Raised when authentication fails."""


class Authentication:

    def __init__(
        self,
        email: str,
        password: str,
        region: str = DEFAULT_REGION,
        timeout: int = 30,
    ) -> None:

        self.email = email
        self.password = password
        self.region = region.lower()

        self.base_url = f"https://cqr-api-{self.region}.hzhjcl.com"

        self.client = httpx.Client(timeout=timeout)

        self.token: str | None = None
        self.refresh_token: str | None = None

    # -----------------------------------------------------

    @staticmethod
    def timestamp() -> str:
        """
        CarLinko expects milliseconds.
        """
        return str(int(time.time() * 1000))

    # -----------------------------------------------------

    @staticmethod
    def _json(data: dict[str, Any]) -> str:
        """
        JSON formatting identical to the mobile app.
        """

        return json.dumps(
            data,
            separators=(",", ":"),
            ensure_ascii=False,
            sort_keys=True,
        )

    # -----------------------------------------------------

    @classmethod
    def sign(
        cls,
        payload: dict[str, Any],
        timestamp: str,
    ) -> str:
        """
        Generate HMAC signature.

        This follows the algorithm recovered from the dashboard.
        """

        message = cls._json(payload) + timestamp

        digest = hmac.new(
            SIGN_KEY.encode(),
            message.encode(),
            hashlib.sha256,
        ).digest()

        return base64.b64encode(digest).decode()

    # -----------------------------------------------------

    def headers(
        self,
        payload: dict[str, Any],
    ) -> dict[str, str]:

        ts = self.timestamp()

        headers = {
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "timestamp": ts,
            "sign": self.sign(payload, ts),
        }

        if self.token:
            headers["token"] = self.token

        return headers

    # -----------------------------------------------------

    def login(self) -> str:

        payload = {
            "email": self.email,
            "password": self.password,
        }

        response = self.client.post(
            f"{self.base_url}/user/login",
            json=payload,
            headers=self.headers(payload),
        )

        if response.status_code != 200:
            raise AuthenticationError(
                f"HTTP {response.status_code}"
            )

        data = response.json()

        # Dashboard returns token inside data{}
        if "data" in data:
            data = data["data"]

        token = data.get("token")

        if not token:
            raise AuthenticationError(data)

        self.token = token
        self.refresh_token = data.get("refreshToken")

        return token

    # -----------------------------------------------------

    def logout(self) -> None:

        self.token = None
        self.refresh_token = None

    # -----------------------------------------------------

    @property
    def authenticated(self) -> bool:
        return self.token is not None
