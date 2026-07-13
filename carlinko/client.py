"""
carlinko/client.py

Main CarLinko API client.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from .auth import Authentication
from .exceptions import (
    ApiError,
    AuthenticationError,
)
from .models import Vehicle

_LOGGER = logging.getLogger(__name__)


class CarLinkoClient:
    """
    Primary CarLinko client.

    Example
    -------
    >>> client = CarLinkoClient(
    ...     email="user@email.com",
    ...     password="password",
    ...     region="sea",
    ... )
    ...
    >>> client.login()
    >>> vehicles = client.get_vehicles()
    """

    def __init__(
        self,
        email: str,
        password: str,
        region: str = "sea",
        timeout: int = 30,
    ) -> None:

        self.auth = Authentication(
            email=email,
            password=password,
            region=region,
            timeout=timeout,
        )

        self.base_url = self.auth.base_url
        self.client = self.auth.client

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def login(self) -> str:
        """Authenticate with CarLinko."""
        return self.auth.login()

    def logout(self) -> None:
        """Forget the current token."""
        self.auth.logout()

    @property
    def authenticated(self) -> bool:
        return self.auth.authenticated

    # ------------------------------------------------------------------
    # Internal request helper
    # ------------------------------------------------------------------

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict:

        payload = json or {}

        response = self.client.request(
            method,
            f"{self.base_url}{endpoint}",
            params=params,
            json=json,
            headers=self.auth.headers(payload),
        )

        if response.status_code == 401:
            raise AuthenticationError("Authentication expired")

        if response.status_code >= 400:
            raise ApiError(
                f"{response.status_code}: {response.text}"
            )

        body = response.json()

        #
        # CarLinko normally wraps responses as:
        #
        # {
        #   "code":200,
        #   "msg":"success",
        #   "data":{...}
        # }
        #

        if isinstance(body, dict):

            code = body.get("code")

            if code not in (0, 200, None):
                raise ApiError(body.get("msg", body))

            return body.get("data", body)

        return body

    # ------------------------------------------------------------------
    # User
    # ------------------------------------------------------------------

    def get_profile(self) -> dict:
        """
        Return logged-in user information.
        """
        return self.request(
            "GET",
            "/user/info",
        )

    # ------------------------------------------------------------------
    # Vehicles
    # ------------------------------------------------------------------

    def get_vehicles(self) -> list[Vehicle]:
        """
        Retrieve every vehicle on the account.
        """

        data = self.request(
            "GET",
            "/user/vehicle",
        )

        if not data:
            return []

        vehicles = []

        for item in data:

            vehicles.append(
                Vehicle.from_api(item)
            )

        return vehicles

    def get_vehicle(self, vehicle_id: str) -> Vehicle:

        vehicles = self.get_vehicles()

        for vehicle in vehicles:

            if vehicle.id == vehicle_id:
                return vehicle

        raise ApiError(
            f"Vehicle '{vehicle_id}' not found"
        )

    # ------------------------------------------------------------------
    # Generic endpoint
    # ------------------------------------------------------------------

    def raw(
        self,
        endpoint: str,
        method: str = "GET",
        *,
        json: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        """
        Call any endpoint.

        Very useful while reverse engineering.
        """

        return self.request(
            method,
            endpoint,
            json=json,
            params=params,
        )

    # ------------------------------------------------------------------
    # Vehicle status
    # ------------------------------------------------------------------

    def get_vehicle_status(
        self,
        vehicle_id: str,
    ) -> dict:
        """
        Placeholder until we discover the
        telemetry endpoint.
        """

        return self.raw(
            f"/user/vehicle/status/{vehicle_id}"
        )

    # ------------------------------------------------------------------
    # WebSocket
    # ------------------------------------------------------------------

    def get_websocket_info(
        self,
        device_sn: str,
    ) -> dict:

        return self.raw(
            f"/netty/getConnect/2/{device_sn}"
        )
