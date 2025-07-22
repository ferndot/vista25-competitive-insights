"""
Agent state models for competitive intelligence system
"""

from typing import Dict, List, Optional, TypedDict, Literal
from pydantic import BaseModel


class CompetitiveIntelligenceState(TypedDict):
    """State model for the competitive intelligence agent workflow"""
    companies: List[str]
    days_back: int
    current_company: Optional[str]
    fetched_articles: Dict[str, List]
    extracted_signals: List[Dict]
    total_articles: int
    total_signals: int
    errors: List[str]
    status: Literal["pending", "fetching", "analyzing", "storing", "complete", "error"]
    progress: str
    results: Dict
