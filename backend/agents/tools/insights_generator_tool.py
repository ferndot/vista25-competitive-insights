"""
Insights generation tool for the Competitive Intelligence Agent
"""

from typing import List, Dict, Any
from datetime import datetime

from langchain_core.tools import tool


@tool
def generate_insights_summary(signals: List[Dict], companies: List[str]) -> Dict[str, Any]:
    """
    Generate strategic insights from collected signals.
    
    This tool allows the agent to synthesize findings and provide
    actionable intelligence.
    """
    try:
        # Analyze signal patterns
        signal_analysis = {
            "total_signals": len(signals),
            "companies_analyzed": len(companies),
            "companies_with_signals": len(set(s.get("company_name") for s in signals)),
            "signal_types": {},
            "impact_distribution": {},
            "confidence_distribution": {},
            "trends": []
        }
        
        # Categorize signals
        for signal in signals:
            # By signal_type
            signal_type = signal.get("signal_type", "unknown")
            signal_analysis["signal_types"][signal_type] = signal_analysis["signal_types"].get(signal_type, 0) + 1
            
            # By impact
            impact = signal.get("impact", "unknown")
            signal_analysis["impact_distribution"][impact] = signal_analysis["impact_distribution"].get(impact, 0) + 1
            
            # By confidence
            confidence = signal.get("confidence", "unknown")
            signal_analysis["confidence_distribution"][confidence] = signal_analysis["confidence_distribution"].get(confidence, 0) + 1
        
        # Identify trends
        if signal_analysis["signal_types"].get("layoffs", 0) > 1:
            signal_analysis["trends"].append("Multiple layoffs detected - possible industry downturn")
        
        if signal_analysis["signal_types"].get("funding", 0) > 1:
            signal_analysis["trends"].append("Active funding environment - growth opportunities")
        
        if signal_analysis["signal_types"].get("acquisition", 0) > 0:
            signal_analysis["trends"].append("M&A activity detected - market consolidation")
        
        # Generate recommendations
        recommendations = []
        
        # High-impact signal recommendations
        high_impact = [s for s in signals if s.get("impact") == "high"]
        if high_impact:
            recommendations.append({
                "priority": "critical",
                "action": f"Immediate follow-up required for {len(high_impact)} high-impact signals",
                "affected_companies": list(set(s.get("company_name") for s in high_impact))
            })
        
        # Leadership change recommendations
        leadership_signals = [s for s in signals if s.get("signal_type") == "leadership"]
        if leadership_signals:
            recommendations.append({
                "priority": "high",
                "action": "Executive outreach recommended - leadership changes detected",
                "affected_companies": list(set(s.get("company_name") for s in leadership_signals))
            })
        
        # Funding opportunity recommendations
        funding_signals = [s for s in signals if s.get("signal_type") == "funding"]
        if funding_signals:
            recommendations.append({
                "priority": "medium",
                "action": "Upselling opportunity - companies with new funding",
                "affected_companies": list(set(s.get("company_name") for s in funding_signals))
            })
        
        return {
            "success": True,
            "analysis": signal_analysis,
            "recommendations": recommendations,
            "key_insights": signal_analysis["trends"],
            "companies_needing_attention": [
                s.get("company_name") for s in signals 
                if s.get("impact") == "high"
            ][:5],  # Top 5
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "analysis": {},
            "recommendations": []
        }
