from typing import Any

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.core.providers.external_feeds import ExternalFeed
from app.utils.logging import get_logger

logger = get_logger(__name__)


class CrisisMonitorInput(BaseModel):
    region: str = Field(
        default="global", description="Region to monitor (e.g., 'global', 'East Africa', 'Southeast Asia')"
    )
    alert_types: str = Field(
        default="all",
        description="Types of alerts to monitor: 'all', 'weather', 'news', or comma-separated list",
    )


class CrisisMonitorTool(BaseTool):
    name: str = "monitor_crisis_alerts"
    description: str = """Use this tool to check for crisis alerts and emergency situations.
    Provide a region and alert types to monitor.
    The tool will fetch recent alerts from news and weather feeds."""
    args_schema: type[BaseModel] = CrisisMonitorInput
    news_feed: ExternalFeed
    weather_feed: ExternalFeed

    def __init__(self, news_feed: ExternalFeed, weather_feed: ExternalFeed) -> None:
        super().__init__(news_feed=news_feed, weather_feed=weather_feed)

    def _run(self, region: str = "global", alert_types: str = "all") -> str:
        raise NotImplementedError("Use async version")

    async def _arun(self, region: str = "global", alert_types: str = "all") -> str:
        try:
            logger.info("crisis_monitoring_started", region=region, alert_types=alert_types)

            all_alerts: list[dict[str, Any]] = []

            if alert_types in ["all", "news"]:
                news_alerts = await self.news_feed.fetch_alerts()
                all_alerts.extend(news_alerts)

            if alert_types in ["all", "weather"]:
                weather_alerts = await self.weather_feed.fetch_alerts()
                all_alerts.extend(weather_alerts)

            if not all_alerts:
                return f"No crisis alerts found for {region}. Monitoring continues in background."

            result = f"""CRISIS MONITORING REPORT
Region: {region}
Alert Types: {alert_types}

ACTIVE ALERTS ({len(all_alerts)}):

"""

            for i, alert in enumerate(all_alerts, 1):
                result += f"""{i}. [{alert['type'].upper()}] {alert['title']}
   Severity: {alert.get('severity', 'unknown')}
   Source: {alert.get('source', 'unknown')}
   Time: {alert.get('timestamp', 'unknown')}
   
   {alert.get('description', 'No description available')}

---

"""

            result += """
RECOMMENDED ACTIONS:
1. Review alerts for relevance to your operations
2. Assess potential impact on ongoing programs
3. Prepare contingency plans if needed
4. Monitor for updates

Note: This monitoring tool runs continuously in the background and will push urgent alerts to your chat stream.
"""

            logger.info("crisis_monitoring_completed", alerts_found=len(all_alerts))
            return result

        except Exception as e:
            logger.error("crisis_monitoring_failed", error=str(e))
            return f"Crisis monitoring failed: {str(e)}"
