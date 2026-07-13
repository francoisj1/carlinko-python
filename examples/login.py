

"""
examples/login.py

Simple test program for the CarLinko SDK.
"""

from pprint import pprint

from carlinko import CarLinkoClient


client = CarLinkoClient(
    email="xxx",
    password="xxxx",
    region="saf",
    debug=True,
)

try:

    print("===================================")
    print("CARLINKO SDK TEST")
    print("===================================\n")

    #
    # Login
    #
    print("Logging in...")

    token = client.login()

    print("✓ Login successful")
    print(f"Token: {token}")

    #
    # User Profile
    #
    print("\n===================================")
    print("USER PROFILE")
    print("===================================")

    profile = client.get_profile()
    pprint(profile)

    #
    # Vehicles
    #
    print("\n===================================")
    print("VEHICLES")
    print("===================================")

    vehicles = client.get_vehicles()

    print(f"\nFound {len(vehicles)} vehicle(s)\n")

    for i, vehicle in enumerate(vehicles, start=1):

        print("-----------------------------------")
        print(f"Vehicle {i}")
        print("-----------------------------------")

        pprint(vehicle)

    #
    # Raw vehicle JSON
    #
    print("\n===================================")
    print("RAW /user/vehicle RESPONSE")
    print("===================================")

    raw = client.raw("/user/vehicle")

    pprint(raw)

    #
    # Terminal Information
    #
    print("\n===================================")
    print("TERMINAL INFORMATION")
    print("===================================")

    for vehicle in vehicles:

        print(f"\nVehicle ID : {vehicle.id}")
        print(f"VIN        : {vehicle.vin}")

        terminal = client.get_terminal(vehicle.id)

        pprint(terminal)

        if isinstance(terminal, dict):

            print("\nPossible Device Identifiers")

            for field in sorted(terminal.keys()):

                if any(
                    word in field.lower()
                    for word in (
                        "device",
                        "terminal",
                        "imei",
                        "sn",
                        "serial",
                        "box",
                    )
                ):
                    print(f"{field:30}: {terminal[field]}")

    #
    # WebSocket Discovery
    #
    print("\n===================================")
    print("WEBSOCKET DISCOVERY")
    print("===================================")

    if raw:

        vehicle = raw[0]

        for field in (
            "deviceId",
            "deviceName",
            "deviceSn",
            "terminalNo",
            "terminalId",
        ):

            if field in vehicle:

                print(f"\nTrying {field}: {vehicle[field]}")

                try:

                    result = client.get_websocket(vehicle[field])

                    print("✓ Success")

                    pprint(result)

                except Exception as e:

                    print(f"✗ Failed: {e}")

    #
    # Complete
    #
    print("\n===================================")
    print("TEST COMPLETE")
    print("===================================")

except Exception:

    print("\n===================================")
    print("ERROR")
    print("===================================")

    import traceback

    traceback.print_exc()
