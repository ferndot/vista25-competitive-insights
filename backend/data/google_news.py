import time
from datetime import datetime, timedelta
from urllib.parse import quote_plus

import feedparser
from loguru import logger

from models.data_source import Result, SourceType
from .base import DataSource


class GoogleNewsSource(DataSource):
    """Google News RSS data source"""
    
    platform_name = "Google News"
    platform_id = "google_news"
    
    def __init__(self):
        super().__init__()
    
    def fetch(self, company_name: str, days_back: int = 7) -> list[Result]:
        """Fetch recent news for a company from Google News RSS"""

        # Build search query with relevant business signals
        search_terms = [
            f'"{company_name}"',
            "(CEO OR CFO OR CTO)",
            "OR funding OR raised OR Series",
            "OR acquisition OR acquired OR merger",
            "OR layoffs OR restructuring",
            "OR partnership OR partners",
        ]

        query = " ".join(search_terms)
        encoded_query = quote_plus(query)

        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

        logger.info(f"Fetching news for {company_name} from Google News RSS")

        try:
            feed = feedparser.parse(url)

            # Check if feed was parsed successfully
            if feed.bozo:
                logger.warning(f"Feed parsing had issues: {feed.bozo_exception}")

            articles = []
            cutoff_date = datetime.now() - timedelta(days=days_back)

            for entry in feed.entries[:20]:  # Get more entries, filter later
                # Parse publication date - fixed for feedparser 6.0.11
                pub_date = None

                # Method 1: Use published_parsed if available
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        pub_date = datetime.fromtimestamp(
                            time.mktime(entry.published_parsed)
                        )
                    except Exception as e:
                        logger.debug(f"Could not parse published_parsed: {e}")

                # Method 2: Parse the published string if method 1 failed
                if not pub_date and hasattr(entry, "published"):
                    try:
                        # Try parsing common date formats
                        from dateutil import parser as date_parser

                        pub_date = date_parser.parse(entry.published)
                    except Exception as e:
                        logger.debug(f"Could not parse published string: {e}")

                # Skip if we couldn't parse the date
                if not pub_date:
                    logger.debug(
                        f"Skipping article with unparseable date: {entry.get('title', 'Unknown')}"
                    )
                    continue

                # Skip old articles
                if pub_date < cutoff_date:
                    continue

                # Extract clean text from summary
                summary = self._clean_html(entry.get("summary", ""))

                article = Result(
                    title=entry.get("title", "No title"),
                    link=entry.get("link", ""),
                    published=entry.get("published", "Unknown date"),
                    published_on=pub_date,
                    source_type=SourceType.news,
                    text=f"{entry.get('title', '')}. {summary}",
                    platform=self.platform_id,
                    platform_name=self.platform_name
                )

                articles.append(article)

            logger.info(f"Found {len(articles)} articles for {company_name} from Google News")
            return articles

        except Exception as e:
            logger.error(f"Error fetching news for {company_name} from Google News: {e}")
            return []
    
    def _extract_source(self, title: str) -> str:
        """Extract source from Google News title format"""
        # Google News format: "Article Title - Source Name"
        parts = title.split(" - ")
        if len(parts) >= 2:
            return parts[-1]
        return "Unknown"
