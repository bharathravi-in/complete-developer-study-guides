#!/usr/bin/env python3
"""
Async API Caller

Demonstrates real-world async patterns for API calls.
Uses httpbin.org for testing (no API key needed).
"""

import asyncio
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import json

# Note: In production, use aiohttp
# pip install aiohttp

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False


@dataclass
class APIResponse:
    """Represents an API response"""
    url: str
    status: int
    data: Optional[Dict[str, Any]]
    error: Optional[str] = None
    elapsed_ms: float = 0


class AsyncAPIClient:
    """Async API client with rate limiting and error handling"""
    
    def __init__(
        self,
        base_url: str = "https://httpbin.org",
        max_concurrent: int = 5,
        timeout: float = 10.0
    ):
        self.base_url = base_url
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
    
    @asynccontextmanager
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        try:
            yield self._session
        except Exception:
            raise
    
    async def close(self):
        """Close the client session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get(self, endpoint: str, params: Dict = None) -> APIResponse:
        """Make GET request with rate limiting"""
        url = f"{self.base_url}{endpoint}"
        start = time.perf_counter()
        
        async with self.semaphore:
            try:
                async with self._get_session() as session:
                    async with session.get(url, params=params) as response:
                        elapsed = (time.perf_counter() - start) * 1000
                        
                        if response.status == 200:
                            data = await response.json()
                            return APIResponse(
                                url=url,
                                status=response.status,
                                data=data,
                                elapsed_ms=elapsed
                            )
                        else:
                            return APIResponse(
                                url=url,
                                status=response.status,
                                data=None,
                                error=f"HTTP {response.status}",
                                elapsed_ms=elapsed
                            )
            except asyncio.TimeoutError:
                return APIResponse(
                    url=url,
                    status=0,
                    data=None,
                    error="Timeout",
                    elapsed_ms=(time.perf_counter() - start) * 1000
                )
            except Exception as e:
                return APIResponse(
                    url=url,
                    status=0,
                    data=None,
                    error=str(e),
                    elapsed_ms=(time.perf_counter() - start) * 1000
                )
    
    async def post(self, endpoint: str, data: Dict) -> APIResponse:
        """Make POST request"""
        url = f"{self.base_url}{endpoint}"
        start = time.perf_counter()
        
        async with self.semaphore:
            try:
                async with self._get_session() as session:
                    async with session.post(url, json=data) as response:
                        elapsed = (time.perf_counter() - start) * 1000
                        response_data = await response.json()
                        return APIResponse(
                            url=url,
                            status=response.status,
                            data=response_data,
                            elapsed_ms=elapsed
                        )
            except Exception as e:
                return APIResponse(
                    url=url,
                    status=0,
                    data=None,
                    error=str(e),
                    elapsed_ms=(time.perf_counter() - start) * 1000
                )
    
    async def fetch_all(self, endpoints: List[str]) -> List[APIResponse]:
        """Fetch multiple endpoints concurrently"""
        tasks = [self.get(endpoint) for endpoint in endpoints]
        return await asyncio.gather(*tasks)


# ============================================
# MOCK CLIENT (when aiohttp not available)
# ============================================

class MockAsyncAPIClient:
    """Mock client that simulates async API calls"""
    
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def close(self):
        pass
    
    async def get(self, endpoint: str, params: Dict = None) -> APIResponse:
        async with self.semaphore:
            start = time.perf_counter()
            await asyncio.sleep(0.1 + (hash(endpoint) % 100) / 1000)
            elapsed = (time.perf_counter() - start) * 1000
            
            return APIResponse(
                url=f"https://mock.api{endpoint}",
                status=200,
                data={"endpoint": endpoint, "mocked": True},
                elapsed_ms=elapsed
            )
    
    async def fetch_all(self, endpoints: List[str]) -> List[APIResponse]:
        tasks = [self.get(endpoint) for endpoint in endpoints]
        return await asyncio.gather(*tasks)


# ============================================
# DEMO
# ============================================

async def demo_single_request():
    """Demo single request"""
    print("\n--- Single Request ---")
    
    if AIOHTTP_AVAILABLE:
        client = AsyncAPIClient()
    else:
        client = MockAsyncAPIClient()
    
    try:
        response = await client.get("/get")
        print(f"URL: {response.url}")
        print(f"Status: {response.status}")
        print(f"Time: {response.elapsed_ms:.1f}ms")
        if response.data:
            print(f"Data keys: {list(response.data.keys())[:5]}")
    finally:
        await client.close()


async def demo_concurrent_requests():
    """Demo concurrent requests"""
    print("\n--- Concurrent Requests ---")
    
    if AIOHTTP_AVAILABLE:
        client = AsyncAPIClient(max_concurrent=10)
    else:
        client = MockAsyncAPIClient(max_concurrent=10)
    
    # Endpoints to fetch
    endpoints = [f"/get?id={i}" for i in range(10)]
    
    try:
        start = time.perf_counter()
        responses = await client.fetch_all(endpoints)
        total_time = time.perf_counter() - start
        
        print(f"Fetched {len(responses)} endpoints")
        print(f"Total time: {total_time:.2f}s")
        print(f"Avg per request: {total_time/len(responses)*1000:.1f}ms")
        
        # Stats
        successful = sum(1 for r in responses if r.status == 200)
        print(f"Successful: {successful}/{len(responses)}")
        
        # Individual times
        for i, r in enumerate(responses[:3]):
            print(f"  {i}: {r.elapsed_ms:.1f}ms")
        print("  ...")
    finally:
        await client.close()


async def demo_rate_limiting():
    """Demo rate limiting with semaphore"""
    print("\n--- Rate Limiting Demo ---")
    
    # Limit to 2 concurrent
    client = MockAsyncAPIClient(max_concurrent=2)
    
    async def timed_fetch(endpoint: str) -> tuple:
        start = time.perf_counter()
        response = await client.get(endpoint)
        return endpoint, time.perf_counter() - start
    
    endpoints = [f"/api/{i}" for i in range(6)]
    
    start = time.perf_counter()
    tasks = [timed_fetch(ep) for ep in endpoints]
    results = await asyncio.gather(*tasks)
    total_time = time.perf_counter() - start
    
    print(f"With max_concurrent=2:")
    print(f"Total time: {total_time:.2f}s")
    print(f"(Would be ~{total_time/3:.2f}s with unlimited)")
    
    await client.close()


async def main():
    print("=" * 60)
    print("ASYNC API CALLER DEMO")
    print("=" * 60)
    
    if not AIOHTTP_AVAILABLE:
        print("\n⚠️  aiohttp not installed. Using mock client.")
        print("   Install with: pip install aiohttp")
    
    await demo_single_request()
    await demo_concurrent_requests()
    await demo_rate_limiting()
    
    print("\n✅ Async API caller demo completed!")


if __name__ == "__main__":
    asyncio.run(main())
