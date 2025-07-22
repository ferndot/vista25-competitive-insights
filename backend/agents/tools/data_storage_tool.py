"""
Data storage tools for the Competitive Intelligence Agent
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from langchain_core.tools import tool

from simple_supabase import SimpleSupabase
from models.tool_params import DataStorageParams


@tool
def store_signals_batch(params: DataStorageParams) -> Dict[str, Any]:
    """
    Store multiple signals in the database efficiently.
    
    This tool allows the agent to make decisions about data persistence
    and handle storage errors gracefully.
    """
    try:
        db = SimpleSupabase()
        
        # Check if table exists
        if not db.check_table_exists():
            return {
                "success": False,
                "error": "Database table not found. Run setup first.",
                "signals_stored": 0
            }
        
        stored_signals = []
        storage_stats = {
            "total_signals": len(params.signals),
            "signals_stored": 0,
            "duplicates_skipped": 0,
            "errors": []
        }
        
        # Process signals in batches
        batch_size = params.batch_size
        for i in range(0, len(params.signals), batch_size):
            batch = params.signals[i:i + batch_size]
            
            for signal in batch:
                try:
                    # Store individual signal
                    result = db.save_signal(signal)
                    
                    if result:
                        stored_signals.append(result)
                        storage_stats["signals_stored"] += 1
                    else:
                        storage_stats["errors"].append(f"Failed to store signal: {signal.get('title', 'unknown')}")
                        
                except Exception as e:
                    if "duplicate" in str(e).lower() or "unique constraint" in str(e).lower():
                        storage_stats["duplicates_skipped"] += 1
                    else:
                        storage_stats["errors"].append(f"Storage error: {str(e)}")
                    continue
        
        return {
            "success": True,
            "signals_stored": storage_stats["signals_stored"],
            "stored_signals": stored_signals,
            "stats": storage_stats,
            "storage_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "signals_stored": 0,
            "stats": {"total_signals": len(params.signals), "signals_stored": 0}
        }


@tool
def get_recent_signals(company_name: Optional[str] = None, limit: int = 10, hours_back: int = 24) -> Dict[str, Any]:
    """
    Retrieve recent signals from the database.
    
    This tool allows the agent to check for existing signals
    and make decisions about data freshness.
    """
    try:
        db = SimpleSupabase()
        
        # Get recent signals
        recent_signals = db.get_recent_signals(limit=limit * 2)  # Get more for filtering
        
        # Filter by company if specified
        if company_name:
            recent_signals = [s for s in recent_signals if s.get("company_name", "").lower() == company_name.lower()]
        
        # Filter by time window
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        filtered_signals = []
        
        for signal in recent_signals:
            detected_at = signal.get("detected_at")
            if detected_at:
                try:
                    signal_time = datetime.fromisoformat(detected_at.replace('Z', '+00:00'))
                    if signal_time >= cutoff_time:
                        filtered_signals.append(signal)
                except:
                    continue
        
        # Limit results
        filtered_signals = filtered_signals[:limit]
        
        return {
            "success": True,
            "company": company_name,
            "signals_found": len(filtered_signals),
            "signals": filtered_signals,
            "metadata": {
                "hours_back": hours_back,
                "limit": limit,
                "query_time": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "signals_found": 0,
            "signals": []
        }
