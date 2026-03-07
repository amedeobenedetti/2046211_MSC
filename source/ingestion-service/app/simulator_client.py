import httpx


class SimulatorClient:

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def get_discovery(self) -> dict:
        url = f"{self.base_url}/api/discovery"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def get_sensor_by_path(self, path: str) -> dict:
        url = f"{self.base_url}{path}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()