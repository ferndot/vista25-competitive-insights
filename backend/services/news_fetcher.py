from typing import List

from loguru import logger

from data.base import DataSource
from data.google_news import GoogleNewsSource
from data.sec import SECFilingsSource
from core.config import settings
from models.data_source import Result


class NewsFetcher:
    """Main class that orchestrates multiple data sources"""

    def __init__(self, sources_list: List[DataSource]= None):
        sources_list = sources_list or [GoogleNewsSource(), SECFilingsSource()]
        self.sources = { src.platform_id:src for src in sources_list}

    def fetch_from_source(self, platform_id: str, company_name: str, days_back: int = 7) -> list[Result]:
        """Fetch data from a specific source"""
        if platform_id not in self.sources:
            logger.error(f"Unknown source: {platform_id}")
            return []
        
        return self.sources[platform_id].fetch(company_name, days_back)

    def fetch_multiple_sources(
        self,
        company_name: str,
        days_back: int = 7,
        sources: list[str] | None = None
    ) -> list[Result]:
        """Fetch from multiple sources and deduplicate"""

        if sources is None:
            sources = list(self.sources.keys())

        all_articles = []

        for source_name in sources:
            if source_name in self.sources:
                articles = self.sources[source_name].fetch(company_name, days_back)
                all_articles.extend(articles)
            else:
                logger.warning(f"Unknown source: {source_name}")

        # Deduplicate by title similarity
        unique_articles = self._deduplicate_articles(all_articles)

        # Sort by date, newest first
        # unique_articles.sort(
        #     key=lambda x: x.published_on, reverse=True
        # )

        return unique_articles

    def get_available_sources(self) -> list[str]:
        """Get list of available data sources"""
        return list(self.sources.keys())

    def add_source(self, name: str, source: DataSource):
        """Add a new data source"""
        self.sources[name] = source

    def remove_source(self, name: str):
        """Remove a data source"""
        if name in self.sources:
            del self.sources[name]

    def _deduplicate_articles(self, articles: list[Result]) -> list[Result]:
        """Remove duplicate articles based on title similarity"""

        seen_titles = set()
        unique = []

        for article in articles:
            # Simple deduplication by first 50 chars of title
            title_key = article.title[:50].lower()

            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique.append(article)

        return unique


# Test the fetcher
if __name__ == "__main__":
    # Example usage with different configurations
    fetcher = NewsFetcher()

    test_companies = ["Salesforce", "Databricks", "OpenAI"]

    for company in test_companies:
        print(f"\n{'=' * 60}")
        print(f"News and data for {company}:")
        print("=" * 60)

        # Test individual sources
        print(f"\n--- Google News ---")
        google_articles = fetcher.fetch_from_source("google_news", company, days_back=3)
        for article in google_articles[:3]:
            print(f"📰 {article.title[:80]}...")
            print(f"   Platform: {article.platform_name} | Type: {article.source_type}")

        # Test combined sources
        print(f"\n--- All Sources Combined ---")
        all_articles = fetcher.fetch_multiple_sources(
            company, 
            days_back=7, 
            sources=["google_news"]
        )

        print(f"Total articles found: {len(all_articles)}")
        for article in all_articles[:5]:
            print(f"📄 {article.title[:80]}...")
            print(f"   Platform: {article.platform_name} | Type: {article.source_type} | Date: {article.published}")

        print("\n" + "-" * 40)
