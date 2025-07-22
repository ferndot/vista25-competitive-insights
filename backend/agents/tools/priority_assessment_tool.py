"""
Priority assessment tool for the Competitive Intelligence Agent
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta

from langchain_core.tools import tool


@tool
def assess_company_priority(
    company_name: str, 
    recent_signals: List[Dict], 
    news_volume: int,
    market_cap_tier: str = "unknown"
) -> Dict[str, Any]:
    """
    Assess the priority level for analyzing a company.
    
    This tool helps the agent make intelligent decisions about
    which companies to prioritize for analysis.
    """
    try:
        priority_score = 0
        priority_factors = []
        
        # Factor 1: Recent high-impact signals
        high_impact_count = len([s for s in recent_signals if s.get("impact") == "high"])
        if high_impact_count > 0:
            priority_score += high_impact_count * 10
            priority_factors.append(f"{high_impact_count} high-impact signals found")
        
        # Factor 2: News volume (activity level)
        if news_volume > 10:
            priority_score += 5
            priority_factors.append(f"High news volume: {news_volume} articles")
        elif news_volume > 5:
            priority_score += 2
            priority_factors.append(f"Moderate news volume: {news_volume} articles")
        
        # Factor 3: Market cap tier (if known)
        tier_scores = {"large": 3, "mid": 2, "small": 1, "unknown": 0}
        tier_score = tier_scores.get(market_cap_tier.lower(), 0)
        priority_score += tier_score
        if tier_score > 0:
            priority_factors.append(f"Market tier: {market_cap_tier}")
        
        # Factor 4: Signal diversity
        signal_types = set(s.get("signal_type") for s in recent_signals if s.get("signal_type"))
        if len(signal_types) > 2:
            priority_score += 3
            priority_factors.append(f"Multiple signal types: {len(signal_types)}")
        
        # Factor 5: Recency of signals
        recent_count = 0
        if recent_signals:
            cutoff = datetime.now() - timedelta(days=1)
            for signal in recent_signals:
                try:
                    signal_time = datetime.fromisoformat(signal.get("detected_at", ""))
                    if signal_time >= cutoff:
                        recent_count += 1
                except:
                    continue
        
        if recent_count > 0:
            priority_score += recent_count * 2
            priority_factors.append(f"{recent_count} signals in last 24h")
        
        # Determine priority level
        if priority_score >= 20:
            priority_level = "critical"
        elif priority_score >= 10:
            priority_level = "high"
        elif priority_score >= 5:
            priority_level = "medium"
        else:
            priority_level = "low"
        
        return {
            "success": True,
            "company": company_name,
            "priority_level": priority_level,
            "priority_score": priority_score,
            "factors": priority_factors,
            "recommendation": {
                "analyze_immediately": priority_level in ["critical", "high"],
                "suggested_depth": "thorough" if priority_level == "critical" else "standard",
                "estimated_signals": max(1, len(recent_signals) + (news_volume // 5))
            },
            "assessment_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "company": company_name,
            "priority_level": "low",
            "priority_score": 0
        }
