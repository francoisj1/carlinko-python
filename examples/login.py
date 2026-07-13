from carlinko import CarLinkoClient

client = CarLinkoClient(
    email="773cascades@gmail.com",
    password="sE9DVP3Q",
    region="ZA",      # We'll verify this
)

try:
    token = client.login()

    print("Login successful!")
    print(token)

except Exception as e:
    print(f"Login failed: {e}")
