"""
API Client for AgroVista Backend
Centralized module for all backend API requests
"""

import requests
import streamlit as st
from typing import Optional, Dict, List, Any
import json


class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Make HTTP request to backend API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
            return None
    
    # Terrain endpoints
    def get_terrains(self) -> Optional[List[Dict]]:
        """Get all terrains"""
        return self._make_request("GET", "/terrenos/")
    
    def get_terrain_by_id(self, terrain_id: int) -> Optional[Dict]:
        """Get terrain by ID"""
        return self._make_request("GET", f"/terrenos/{terrain_id}")
    
    def create_terrain(self, terrain_data: Dict) -> Optional[Dict]:
        """Create new terrain"""
        return self._make_request("POST", "/terrenos/", json=terrain_data)
    
    def update_terrain(self, terrain_id: int, terrain_data: Dict) -> Optional[Dict]:
        """Update terrain"""
        return self._make_request("PUT", f"/terrenos/{terrain_id}", json=terrain_data)
    
    def delete_terrain(self, terrain_id: int) -> bool:
        """Delete terrain"""
        result = self._make_request("DELETE", f"/terrenos/{terrain_id}")
        return result is not None
    
    # Parcel endpoints
    def get_parcels(self, terrain_id: Optional[int] = None) -> Optional[List[Dict]]:
        """Get parcels, optionally filtered by terrain"""
        endpoint = "/parcelas/"
        if terrain_id:
            endpoint += f"?terrain_id={terrain_id}"
        return self._make_request("GET", endpoint)
    
    def get_parcel_by_id(self, parcel_id: int) -> Optional[Dict]:
        """Get parcel by ID"""
        return self._make_request("GET", f"/parcelas/{parcel_id}")
    
    def create_parcel(self, parcel_data: Dict) -> Optional[Dict]:
        """Create new parcel"""
        return self._make_request("POST", "/parcelas/", json=parcel_data)
    
    def update_parcel(self, parcel_id: int, parcel_data: Dict) -> Optional[Dict]:
        """Update parcel"""
        return self._make_request("PUT", f"/parcelas/{parcel_id}", json=parcel_data)
    
    def delete_parcel(self, parcel_id: int) -> bool:
        """Delete parcel"""
        result = self._make_request("DELETE", f"/parcelas/{parcel_id}")
        return result is not None
    
    # Activity endpoints
    def get_activities(self, parcel_id: Optional[int] = None) -> Optional[List[Dict]]:
        """Get activities, optionally filtered by parcel"""
        endpoint = "/actividades/"
        if parcel_id:
            endpoint += f"?parcel_id={parcel_id}"
        return self._make_request("GET", endpoint)
    
    def create_activity(self, activity_data: Dict) -> Optional[Dict]:
        """Create new activity"""
        return self._make_request("POST", "/actividades/", json=activity_data)
    
    # Economy endpoints
    def get_transactions(self) -> Optional[List[Dict]]:
        """Get all transactions"""
        return self._make_request("GET", "/economia/transacciones/")
    
    def get_budget_summary(self) -> Optional[Dict]:
        """Get budget summary"""
        return self._make_request("GET", "/economia/presupuesto/")
    
    # Chat endpoints
    def send_chat_message(self, message: str) -> Optional[Dict]:
        """Send message to AI chat assistant"""
        return self._make_request("POST", "/chat/", json={"message": message})
    
    # Dashboard/Analytics endpoints
    def get_dashboard_stats(self) -> Optional[Dict]:
        """Get dashboard statistics"""
        return self._make_request("GET", "/control/dashboard-stats")
    
    def get_terrain_geojson(self, terrain_id: Optional[int] = None) -> Optional[Dict]:
        """Get terrain geometries as GeoJSON"""
        endpoint = "/terrenos/geojson"
        if terrain_id:
            endpoint += f"/{terrain_id}"
        return self._make_request("GET", endpoint)
    
    def get_parcel_geojson(self, terrain_id: Optional[int] = None) -> Optional[Dict]:
        """Get parcel geometries as GeoJSON"""
        endpoint = "/parcelas/geojson"
        if terrain_id:
            endpoint += f"?terrain_id={terrain_id}"
        return self._make_request("GET", endpoint)


# Global API client instance
@st.cache_resource
def get_api_client() -> APIClient:
    """Get cached API client instance"""
    return APIClient()