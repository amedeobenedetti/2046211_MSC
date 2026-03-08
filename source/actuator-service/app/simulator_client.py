import httpx


class SimulatorClient:

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def post_actuator_command(self, actuator_name: str, command: dict) -> dict:
        url = f"{self.base_url}/api/actuators/{actuator_name}"

        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, json=command)
            response.raise_for_status()
        
        return response.json()