"""
Agent tool parameter models for competitive intelligence system
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class NewsQueryParams(BaseModel):
    """Parameters for news fetching"""
    company_name: str = Field(description="Company name to search for")
    days_back: int = Field(7, description="Number of days to look back")
    max_articles: int = Field(20, description="Maximum articles to fetch")
    sources: Optional[List[str]] = Field(None, description="Specific sources to use")


class SignalAnalysisParams(BaseModel):
    """Parameters for signal analysis"""
    company_name: str = Field(description="Company name")
    article_text: str = Field(description="Article text to analyze")
    article_url: Optional[str] = Field(None, description="Source URL")
    confidence_threshold: str = Field("medium", description="Minimum confidence level")


class DataStorageParams(BaseModel):
    """Parameters for data storage"""
    signals: List[Dict] = Field(description="List of signals to store")
    batch_size: int = Field(10, description="Batch size for storage")
