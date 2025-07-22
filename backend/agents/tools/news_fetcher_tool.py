"""
News fetching tool for the Competitive Intelligence Agent
"""

from typing import Dict, Any
from datetime import datetime

from langchain_core.tools import tool

from services.news_fetcher import NewsFetcher
from models.tool_params import NewsQueryParams


@tool
def fetch_company_news(params: NewsQueryParams) -> Dict[str, Any]:
    """
    Fetch news articles for a company using multiple sources.
    
    This tool allows the agent to autonomously collect news data
    and make decisions about which sources to prioritize.
    """
    try:
        fetcher = NewsFetcher()
        
        # Get available sources
        available_sources = fetcher.get_available_sources()
        
        # Use specified sources or all available
        sources_to_use = params.sources or available_sources
        
        # Fetch articles
        articles = fetcher.fetch_multiple_sources(
            company_name=params.company_name,
            days_back=params.days_back,
            sources=sources_to_use
        )
        
        # Limit articles if specified
        if params.max_articles and len(articles) > params.max_articles:
            articles = articles[:params.max_articles]
        
        # Convert to serializable format
        article_data = []
        for article in articles:
            article_data.append({
                "title": article.title,
                "text": article.text,
                "link": article.link,
                "published": article.published,
                "published_on": article.published_on.isoformat() if article.published_on else None,
                "platform_name": article.platform_name,
                "source": article.source.value,
                "relevance_score": len([word for word in params.company_name.lower().split() 
                                       if word in article.text.lower()]) / len(params.company_name.split())
            })
        
        # Sort by relevance and recency
        article_data.sort(key=lambda x: (x["relevance_score"], x["published_on"] or ""), reverse=True)
        
        return {
            "success": True,
            "company": params.company_name,
            "articles_found": len(article_data),
            "sources_used": sources_to_use,
            "articles": article_data,
            "metadata": {
                "fetch_time": datetime.now().isoformat(),
                "days_back": params.days_back,
                "max_articles": params.max_articles
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "company": params.company_name,
            "articles_found": 0,
            "articles": []
        }
