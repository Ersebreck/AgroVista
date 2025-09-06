"""
Unit tests for activity routes.
"""
from fastapi import status


class TestActivityRoutes:
    """Test activity-related API endpoints."""
    
    def test_get_activities_empty(self, client):
        """Test getting activities when none exist."""
        response = client.get("/activities/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_create_activity(self, client, sample_location):
        """Test creating a new activity."""
        activity_data = {
            "name": "Harvesting",
            "description": "Harvest tomatoes",
            "location_id": sample_location.id,
            "date": "2024-07-01",
            "activity_type": "Harvest",
            "status": "Planned"
        }
        
        response = client.post("/activities/", json=activity_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Harvesting"
        assert data["activity_type"] == "Harvest"
        assert data["status"] == "Planned"
        assert "id" in data
    
    def test_get_activities_with_data(self, client, sample_activity):
        """Test getting activities when data exists."""
        response = client.get("/activities/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_activity.name
    
    def test_get_activity_by_id(self, client, sample_activity):
        """Test getting a specific activity by ID."""
        response = client.get(f"/activities/{sample_activity.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == sample_activity.id
        assert data["name"] == sample_activity.name
    
    def test_get_activity_not_found(self, client):
        """Test getting non-existent activity."""
        response = client.get("/activities/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_activity(self, client, sample_activity):
        """Test updating an activity."""
        update_data = {
            "name": "Updated Harvest",
            "status": "Completed"
        }
        
        response = client.put(f"/activities/{sample_activity.id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Updated Harvest"
        assert data["status"] == "Completed"
    
    def test_delete_activity(self, client, sample_activity):
        """Test deleting an activity."""
        response = client.delete(f"/activities/{sample_activity.id}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify it's deleted
        response = client.get(f"/activities/{sample_activity.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_activities_by_location(self, client, sample_activity, sample_location):
        """Test getting activities by location."""
        response = client.get(f"/activities/location/{sample_location.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["location_id"] == sample_location.id
    
    def test_get_activities_by_date_range(self, client, sample_activity):
        """Test getting activities by date range."""
        start_date = "2023-01-01"
        end_date = "2025-12-31"
        
        response = client.get(f"/activities/date-range/{start_date}/{end_date}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 1
    
    def test_create_activity_with_details(self, client, sample_location):
        """Test creating activity with details."""
        activity_data = {
            "name": "Fertilization",
            "description": "Apply NPK fertilizer",
            "location_id": sample_location.id,
            "date": "2024-07-01",
            "activity_type": "Treatment",
            "status": "Planned",
            "details": [
                {
                    "name": "Fertilizer Type",
                    "value": "NPK 20-20-20",
                    "unit": None
                },
                {
                    "name": "Quantity",
                    "value": "50",
                    "unit": "kg"
                }
            ]
        }
        
        response = client.post("/activities/with-details", json=activity_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Fertilization"
        assert len(data["details"]) == 2
        assert data["details"][0]["name"] == "Fertilizer Type"
        assert data["details"][1]["value"] == "50"
    
    def test_get_activity_types(self, client, sample_activity):
        """Test getting unique activity types."""
        response = client.get("/activities/types")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        assert "Maintenance" in data
    
    def test_get_activity_status_options(self, client):
        """Test getting available status options."""
        response = client.get("/activities/status-options")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        assert "Planned" in data
        assert "Completed" in data
        assert "In Progress" in data
        assert "Cancelled" in data
    
    # Test legacy Spanish endpoints
    def test_legacy_get_actividades(self, client, sample_activity):
        """Test legacy Spanish endpoint for getting activities."""
        response = client.get("/actividades/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_activity.name
    
    def test_legacy_crear_actividad(self, client, sample_location):
        """Test legacy Spanish endpoint for creating activity."""
        activity_data = {
            "name": "Siembra",
            "description": "Sembrar maíz",
            "location_id": sample_location.id,
            "date": "2024-07-01",
            "activity_type": "Planting",
            "status": "Planned"
        }
        
        response = client.post("/actividades/", json=activity_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Siembra"
        assert data["activity_type"] == "Planting"
