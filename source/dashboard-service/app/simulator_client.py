import httpx


class HTTPxClient:

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
    
    def get_sensors_list(self) -> dict:
        url = f"{self.base_url}/api/sensors"

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
        
        return response.json()
    
    def get_actuators_list(self) -> dict:
        url = f"{self.base_url}/api/actuators"

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
        
        return response.json()
    
    def request_url(self, url: str, method: str, **kwargs):
        with httpx.Client(timeout=10.0) as client:
            response = client.request(method, url, **kwargs)
            response.raise_for_status()
        
        return response.json()
        