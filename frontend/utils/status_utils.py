"""
Status evaluation utilities for parcels
"""

from typing import List


def convert_status_to_display(status_list: List[str]) -> str:
    """
    Convert raw status list to display status.
    
    Args:
        status_list: List of status strings from parcel evaluation
        
    Returns:
        Display status string ("Optimal", "Attention", "Critical")
    """
    if "Inactive" in status_list or "Inactiva" in status_list:
        return "Critical"
    elif "Pending intervention" in status_list or "Pendiente de intervención" in status_list:
        return "Attention"
    elif "Active" in status_list or "Activa" in status_list:
        return "Optimal"
    else:
        return "Attention"


def get_status_emoji(status_display: str) -> str:
    """
    Get emoji for status display
    
    Args:
        status_display: Display status string
        
    Returns:
        Emoji string for the status
    """
    status_emoji = {
        "Optimal": "✅", 
        "Attention": "⚠️", 
        "Critical": "🚨"
    }
    return status_emoji.get(status_display, "❓")


def get_status_color(status_display: str) -> str:
    """
    Get color for status display
    
    Args:
        status_display: Display status string
        
    Returns:
        Color string for the status
    """
    status_colors = {
        'Optimal': '🟢',
        'Attention': '🟡', 
        'Critical': '🔴'
    }
    return status_colors.get(status_display, '🔵')