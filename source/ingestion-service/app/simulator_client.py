import httpx


class SimulatorClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def get_sensor(self, sensor_name: str) -> dict:
        url = f"{self.base_url}/api/sensors/{sensor_name}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()