from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


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


class SignalType(str, Enum):
    """Business signal types with descriptions for better LLM understanding"""

    def __new__(cls, value, description):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    leadership = (
        "leadership",
        "CEO/CFO/CTO departure or arrival → high churn risk, needs exec engagement",
    )
    funding = (
        "funding",
        "Series A/B/C or funding round → expansion opportunity, budget available",
    )
    acquisition = (
        "acquisition",
        "Company acquired or merged → vendor consolidation risk",
    )
    layoffs = (
        "layoffs",
        "Staff reduction or restructuring → budget concerns, project delays",
    )
    expansion = (
        "expansion",
        "New market/product/geography → opportunity for additional services",
    )
    partnership = (
        "partnership",
        "Strategic partnership announced → potential displacement or integration opportunity",
    )
    none = (
        "none",
        "No actionable signal detected",
    )


class ImpactLevel(str, Enum):
    """Impact level with guidance for CSM prioritization"""

    def __new__(cls, value, description):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    high = (
        "high",
        "Immediate action required within 48 hours",
    )
    medium = (
        "medium",
        "Action required within 1 week",
    )
    low = (
        "low",
        "Monitor and mention in next regular check-in",
    )


class Confidence(str, Enum):
    """Extraction confidence level"""

    def __new__(cls, value, description):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    high = (
        "high",
        "Very clear signal with specific details and credible source",
    )
    medium = (
        "medium",
        "Signal present but some details unclear or source less authoritative",
    )
    low = (
        "low",
        "Weak signal, vague details, or questionable source",
    )


class Signal(BaseModel):
    """Core signal extracted from news/data sources"""

    # Core classification
    type: SignalType = Field(
        description="Primary signal type - choose the most relevant category"
    )

    impact: ImpactLevel = Field(description="Business impact level for prioritization")

    # Key details - only what's essential
    title: str = Field(description="One-line summary (e.g., 'CEO John Smith departed')")

    action: str = Field(
        description="CSM action required (e.g., 'Schedule exec check-in within 48h')"
    )

    # Optional context
    amount: str | None = Field(
        default=None, description="Monetary amount if applicable (e.g., '$50M')"
    )

    person: str | None = Field(
        default=None, description="Key person if applicable (e.g., 'John Smith, CEO')"
    )

    confidence: Confidence = Field(
        description="How confident we are in this signal extraction"
    )


class SignalWithMetadata(Signal):
    """Signal with additional metadata for storage/display"""

    company_name: str
    source_url: str | None = None
    detected_at: datetime = Field(default_factory=datetime.now)
    article_date: datetime | None = None
