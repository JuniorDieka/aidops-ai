from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class ExternalFeed(ABC):
    @abstractmethod
    async def fetch_alerts(self) -> list[dict[str, Any]]:
        pass


class MockNewsFeed(ExternalFeed):
    async def fetch_alerts(self) -> list[dict[str, Any]]:
        import asyncio

        await asyncio.sleep(0.1)
        return [
            {
                "type": "news",
                "title": "[DEMO] Humanitarian Crisis Alert: Simulated Event",
                "description": "This is a mock news alert for demonstration purposes. "
                "In production mode, this would fetch real crisis alerts from news APIs.",
                "severity": "medium",
                "timestamp": datetime.utcnow().isoformat(),
                "source": "Mock News API",
            }
        ]


class MockWeatherFeed(ExternalFeed):
    async def fetch_alerts(self) -> list[dict[str, Any]]:
        import asyncio

        await asyncio.sleep(0.1)
        return [
            {
                "type": "weather",
                "title": "[DEMO] Severe Weather Alert: Simulated Conditions",
                "description": "This is a mock weather alert for demonstration purposes. "
                "In production mode, this would fetch real weather alerts from weather APIs.",
                "severity": "low",
                "timestamp": datetime.utcnow().isoformat(),
                "source": "Mock Weather API",
            }
        ]


class RealNewsFeed(ExternalFeed):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def fetch_alerts(self) -> list[dict[str, Any]]:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://newsapi.org/v2/top-headlines",
                params={
                    "apiKey": self.api_key,
                    "category": "general",
                    "q": "crisis OR disaster OR emergency",
                },
            ) as response:
                data = await response.json()
                alerts = []
                for article in data.get("articles", [])[:5]:
                    alerts.append(
                        {
                            "type": "news",
                            "title": article.get("title", ""),
                            "description": article.get("description", ""),
                            "severity": "medium",
                            "timestamp": article.get("publishedAt", datetime.utcnow().isoformat()),
                            "source": article.get("source", {}).get("name", "Unknown"),
                        }
                    )
                return alerts
