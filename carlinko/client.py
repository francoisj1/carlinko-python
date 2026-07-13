"""
carlinko/client.py

Main CarLinko API client.
"""

from __future__ import annotations

import httpx

from .auth import Authentication
from .exceptions import (
    ApiError,
    AuthenticationError,
    VehicleNotFound,
)
from .models import (
    User,
    Vehicle,
)


class CarLinkoClient:
    """
    Main CarLinko SDK client.
    """

    def __init__(
        self,
        email: str,
        password: str,
        region: str = "saf",
        *,
        timeout: int = 20,
    ):

        #
        # The CarLinko API calls this "account".
        # The SDK exposes it as "email".
        #
        self.auth = Authentication(
            account=email,
            password=password,
            region=region,
            timeout=timeout,
        )

        self.http = self.auth.client

    # -------------------------------------------------------------
    # Authentication
    # -------------------------------------------------------------

    def login(self) -> str:
        """
        Authenticate against CarLinko.

        Returns
        -------
        str
            Access token.
        """
        return self.auth.login()

    @property
    def token(self) -> str | None:
        return self.auth.token

    @property
    def authenticated(self) -> bool:
        return self.auth.token is not None

    # -------------------------------------------------------------
    # Generic request
    # -------------------------------------------------------------

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
    ) -> dict:

        body = json or {}

        response = self.http.request(
            method=method,
            url=self.auth.api_base + endpoint,
            params=params,
            json=json,
            headers=self.auth.headers(body),
        )

        response.raise_for_status()

        payload = response.json()

        #
        # Successful responses use:
        #
        # {
        #     "code":"0000",
        #     "msg":"success",
        #     "data": ...
        # }
        #

        code = str(payload.get("code"))

        if code != "0000":
            raise ApiError(
                payload.get("msg", payload)
            )

        return payload.get("data")

    # -------------------------------------------------------------
    # User
    # -------------------------------------------------------------

    def get_profile(self) -> User:

        data = self.request(
            "GET",
            "/user/info",
        )

        return User.from_api(data)

    # -------------------------------------------------------------
    # Vehicles
    # -------------------------------------------------------------

    def get_vehicles(self) -> list[Vehicle]:

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

    def get_vehicle(
        self,
        vehicle_id: str,
    ) -> Vehicle:

        for vehicle in self.get_vehicles():

            if vehicle.id == vehicle_id:
                return vehicle

        raise VehicleNotFound(vehicle_id)

    # -------------------------------------------------------------
    # Terminal
    # -------------------------------------------------------------

    def get_terminal(
        self,
        vehicle_id: str,
    ) -> dict:

        return self.request(
            "GET",
            f"/user/vehicle/terminal/{vehicle_id}",
        )

    # -------------------------------------------------------------
    # WebSocket
    # -------------------------------------------------------------

    def get_websocket(
        self,
        device_sn: str,
    ) -> dict:

        return self.request(
            "GET",
            f"/netty/getConnect/2/{device_sn}",
        )

    # -------------------------------------------------------------
    # Raw API
    # -------------------------------------------------------------

    def raw(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        params: dict | None = None,
        json: dict | None = None,
    ) -> dict:

        return self.request(
            method,
            endpoint,
            params=params,
            json=json,
        )
