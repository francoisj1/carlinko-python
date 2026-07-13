"""
carlinko/websocket.py

CarLinko realtime telemetry client.
"""

from __future__ import annotations

import json
import threading
import time
import websocket


class CarLinkoWebSocket:
    """
    CarLinko realtime websocket client.

    Usage:

        ws = CarLinkoWebSocket(
            url=ws_url,
            token=token,
            vehicle_id=vehicle.id,
            device_sn=device_sn,
            debug=True,
        )

        ws.add_callback(print)
        ws.connect()
    """

    def __init__(
        self,
        url: str,
        token: str,
        vehicle_id: str,
        device_sn: str,
        *,
        debug: bool = False,
    ):

        self.url = (
            url.replace("http://", "ws://")
               .replace("https://", "wss://")
        )

        self.token = token
        self.vehicle_id = str(vehicle_id)
        self.device_sn = device_sn

        self.debug = debug

        self.ws = None
        self.connected = False
        self.callbacks = []

    # ---------------------------------------------------------

    def add_callback(self, callback):
        self.callbacks.append(callback)

    # ---------------------------------------------------------

    def connect(self):

        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

        threading.Thread(
            target=self.ws.run_forever,
            daemon=True,
        ).start()

    # ---------------------------------------------------------

    def close(self):

        if self.ws:
            self.ws.close()

    # ---------------------------------------------------------

    def send(self, payload):

        if isinstance(payload, dict):
            payload = json.dumps(payload)

        if self.debug:
            print("\nSEND")
            print(payload)

        self.ws.send(payload)

    # ---------------------------------------------------------

    def authenticate(self):

        self.send(
            {
                "action": 1,
                "data": {
                    "token": self.token,
                    "vehicleId": self.vehicle_id,
                },
            }
        )

    # ---------------------------------------------------------

    def subscribe(self):

        self.send(
            {
                "action": 0,
                "data": {
                    "sn": self.device_sn,
                },
            }
        )

    # ---------------------------------------------------------

    def request_telemetry(self):

        self.send(
            {
                "action": 6
            }
        )

    # ---------------------------------------------------------

    def _on_open(self, ws):

        self.connected = True

        print("✓ WebSocket connected")

        #
        # Login
        #
        self.authenticate()

        time.sleep(0.5)

        #
        # Subscribe
        #
        self.subscribe()

        time.sleep(0.5)

        #
        # Request telemetry
        #
        self.request_telemetry()

    # ---------------------------------------------------------

    def _on_message(self, ws, message):

        if self.debug:

            print("\nRECEIVED")
            print(message)

        try:
            packet = json.loads(message)
        except Exception:
            packet = message

        #
        # Forward packet to all listeners.
        #

        for callback in self.callbacks:
            callback(packet)

    # ---------------------------------------------------------

    def _on_error(self, ws, error):

        print("\nWebSocket error")
        print(error)

    # ---------------------------------------------------------

    def _on_close(
        self,
        ws,
        status_code,
        message,
    ):

        self.connected = False

        print(
            f"\nWebSocket closed "
            f"({status_code}) {message}"
        )

    # ---------------------------------------------------------

    def run_forever(self):

        self.connect()

        while True:
            time.sleep(1)
