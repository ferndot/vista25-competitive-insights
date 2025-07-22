"""
Data source models for competitive intelligence system
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """Data source types with characteristics"""
    
    def __new__(cls, value, description):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj
    
    news = (
        "news",
        "Public news articles from media outlets - may contain speculation or bias",
    )
    regulatory = (
        "regulatory", 
        "Official SEC filings and regulatory documents - highly reliable and material",
    )
    social = (
        "social",
        "Social media posts and updates - timely but requires verification",
    )
    industry = (
        "industry",
        "Industry reports and analyst coverage - expert perspective",
    )
    internal = (
        "internal",
        "Internal company communications or documents - authoritative",
    )


class Result(BaseModel):
    """Standard data structure returned by all data sources"""
    
    title: str = Field(description="Article/post title")
    link: str = Field(description="URL to the original content")
    published: str = Field(description="Original publication date string")
    published_on: datetime = Field(description="Parsed publication datetime")
    source_type: SourceType = Field(description="Type of content source")
    text: str = Field(description="Full text content for signal extraction")
    platform: str = Field(description="Platform identifier (e.g., 'google_news', 'twitter')")
    platform_name: str = Field(description="Human-readable platform name (e.g., 'Google News', 'Twitter')")
