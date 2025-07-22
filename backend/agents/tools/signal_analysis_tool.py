"""
Signal analysis tools for the Competitive Intelligence Agent
"""

import os
from typing import List, Dict, Any
from datetime import datetime

from langchain_core.tools import tool

from agents.signal_detector import SignalDetector
from models.tool_params import SignalAnalysisParams


@tool
def analyze_article_for_signals(params: SignalAnalysisParams) -> Dict[str, Any]:
    """
    Analyze a single article for business signals.
    
    This tool gives the agent fine-grained control over signal extraction
    and allows it to make decisions about confidence thresholds.
    """
    try:
        detector = SignalDetector(api_key=os.environ.get("OPENAI_API_KEY", ""))
        
        # Extract signal
        signal = detector.extract(params.company_name, params.article_text)
        
        if not signal:
            return {
                "success": True,
                "signal_found": False,
                "company": params.company_name,
                "reason": "No actionable signal detected"
            }
        
        # Check confidence threshold
        confidence_levels = {"low": 0, "medium": 1, "high": 2}
        signal_confidence = confidence_levels.get(signal.confidence.value, 0)
        threshold_confidence = confidence_levels.get(params.confidence_threshold, 1)
        
        if signal_confidence < threshold_confidence:
            return {
                "success": True,
                "signal_found": False,
                "company": params.company_name,
                "reason": f"Signal confidence {signal.confidence.value} below threshold {params.confidence_threshold}",
                "extracted_signal": signal.dict()
            }
        
        # Convert signal to dict and add metadata
        signal_dict = signal.dict()
        signal_dict.update({
            "company_name": params.company_name,
            "source_url": params.article_url,
            "detected_at": datetime.now().isoformat(),
            "analysis_metadata": {
                "confidence_threshold": params.confidence_threshold,
                "article_length": len(params.article_text),
                "extraction_time": datetime.now().isoformat()
            }
        })
        
        return {
            "success": True,
            "signal_found": True,
            "company": params.company_name,
            "signal": signal_dict,
            "impact_level": signal.impact.value,
            "signal_type": signal.type.value,
            "confidence": signal.confidence.value
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "signal_found": False,
            "company": params.company_name
        }


@tool
def batch_analyze_articles(company_name: str, articles: List[Dict], confidence_threshold: str = "medium") -> Dict[str, Any]:
    """
    Analyze multiple articles at once for efficiency.
    
    This tool allows the agent to process articles in batches
    and make decisions about prioritization.
    """
    try:
        detector = SignalDetector(api_key=os.environ.get("OPENAI_API_KEY", ""))
        
        signals_found = []
        processing_stats = {
            "total_articles": len(articles),
            "articles_processed": 0,
            "signals_extracted": 0,
            "high_impact_signals": 0,
            "errors": []
        }
        
        for article in articles:
            try:
                # Analyze each article
                signal = detector.extract(company_name, article.get("text", ""))
                processing_stats["articles_processed"] += 1
                
                if signal:
                    # Check confidence threshold
                    confidence_levels = {"low": 0, "medium": 1, "high": 2}
                    signal_confidence = confidence_levels.get(signal.confidence.value, 0)
                    threshold_confidence = confidence_levels.get(confidence_threshold, 1)
                    
                    if signal_confidence >= threshold_confidence:
                        signal_dict = signal.dict()
                        signal_dict.update({
                            "company_name": company_name,
                            "source_url": article.get("link"),
                            "detected_at": datetime.now().isoformat(),
                            "article_title": article.get("title", ""),
                            "article_date": article.get("published_on")
                        })
                        
                        signals_found.append(signal_dict)
                        processing_stats["signals_extracted"] += 1
                        
                        if signal.impact.value == "high":
                            processing_stats["high_impact_signals"] += 1
                            
            except Exception as e:
                processing_stats["errors"].append(f"Error processing article: {str(e)}")
                continue
        
        return {
            "success": True,
            "company": company_name,
            "signals": signals_found,
            "stats": processing_stats,
            "processing_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "company": company_name,
            "signals": [],
            "stats": {"total_articles": len(articles), "articles_processed": 0, "signals_extracted": 0}
        }
