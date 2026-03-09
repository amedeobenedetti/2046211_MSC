# import httpx
# from httpx_sse import connect_sse


# class SimulatorClient:

#     def __init__(self, base_url: str):
#         self.base_url = base_url.rstrip("/")

#     async def get_discovery(self) -> dict:
#         url = f"{self.base_url}/api/discovery"

#         async with httpx.AsyncClient(timeout=10.0) as client:
#             response = await client.get(url)
#             response.raise_for_status()
#             return response.json()

#     async def get_sensor_by_path(self, path: str) -> dict:
#         url = f"{self.base_url}{path}"

#         async with httpx.AsyncClient(timeout=10.0) as client:
#             response = await client.get(url)
#             response.raise_for_status()
#             return response.json()
        
#     async def get_telemetry_topics(self) -> list[str]:
#         url = f"{self.base_url}/api/telemetry/topics"

#         async with httpx.AsyncClient(timeout=10.0) as client:
#             response = await client.get(url)
#             response.raise_for_status()
#             return response.json()["topics"]

#     # async def stream_telemetry(self, topic: str):
#     #     url = f"{self.base_url}/api/telemetry/stream/{topic}"

#     #     async with httpx.AsyncClient(timeout=None) as client:
#     #         async with client.stream("GET", url) as response:
#     #             async for line in response.aiter_lines():

#     #                 if not line.startswith("data:"):
#     #                     continue

#     #                 payload = line.replace("data:", "").strip()

#     #                 yield payload
                    
#     async def stream_telemetry(self, topic: str):
#         url = f"{self.base_url}/api/telemetry/stream/{topic}"

#         async with httpx.AsyncClient(timeout=None) as client:
#             async with connect_sse(client, "GET", url) as event_source:
#                 return event_source

import httpx
import logging

logger = logging.getLogger(__name__)

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

    async def get_telemetry_topics(self) -> list[str]:
        url = f"{self.base_url}/api/telemetry/topics"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()["topics"]

    async def stream_telemetry(self, topic: str):
        url = f"{self.base_url}/api/telemetry/stream/{topic}"
        
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    # print(line, flush=True)
                    if not line:
                        continue
                    if not line.startswith("data:"):
                        continue
                    payload = line[5:].strip()
                    if not payload:
                        continue
                    yield payload
                    