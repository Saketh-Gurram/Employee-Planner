"""In-memory storage for analysis results (no database needed)"""
from typing import Dict, Any, Optional
from datetime import datetime

# Global in-memory storage
analysis_storage: Dict[str, Dict[str, Any]] = {}

def save_analysis(analysis_id: str, data: Dict[str, Any]) -> None:
    """Save analysis to memory"""
    analysis_storage[analysis_id] = {
        **data,
        "analysis_id": analysis_id,
        "updated_at": datetime.utcnow().isoformat()
    }

def get_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    """Get analysis from memory"""
    return analysis_storage.get(analysis_id)

def update_analysis_status(analysis_id: str, status: str, **kwargs) -> None:
    """Update analysis status and other fields"""
    if analysis_id in analysis_storage:
        analysis_storage[analysis_id]["status"] = status
        analysis_storage[analysis_id]["updated_at"] = datetime.utcnow().isoformat()
        for key, value in kwargs.items():
            analysis_storage[analysis_id][key] = value
