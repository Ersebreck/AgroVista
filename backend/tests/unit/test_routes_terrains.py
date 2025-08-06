"""
Unit tests for terrain routes.
"""
import pytest
from fastapi import status


class TestTerrainRoutes:
    """Test terrain-related API endpoints."""
    
    def test_get_terrains_empty(self, client):
        """Test getting terrains when none exist."""
        response = client.get("/terrains/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_create_terrain(self, client, sample_user):
        """Test creating a new terrain."""
        terrain_data = {
            "name": "North Farm",
            "description": "Large agricultural land in the north",
            "owner_id": sample_user.id
        }
        
        response = client.post("/terrains/", json=terrain_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "North Farm"
        assert data["description"] == "Large agricultural land in the north"
        assert data["owner_id"] == sample_user.id
        assert "id" in data
    
    def test_get_terrains_with_data(self, client, sample_terrain):
        """Test getting terrains when data exists."""
        response = client.get("/terrains/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_terrain.name
        assert data[0]["id"] == sample_terrain.id
    
    def test_get_terrain_by_id(self, client, sample_terrain):
        """Test getting a specific terrain by ID."""
        response = client.get(f"/terrains/{sample_terrain.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == sample_terrain.id
        assert data["name"] == sample_terrain.name
        assert data["description"] == sample_terrain.description
    
    def test_get_terrain_not_found(self, client):
        """Test getting non-existent terrain."""
        response = client.get("/terrains/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_terrain(self, client, sample_terrain):
        """Test updating a terrain."""
        update_data = {
            "name": "Updated Farm Name",
            "description": "Updated description with more details"
        }
        
        response = client.put(f"/terrains/{sample_terrain.id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Updated Farm Name"
        assert data["description"] == "Updated description with more details"
        assert data["id"] == sample_terrain.id
    
    def test_delete_terrain(self, client, sample_terrain):
        """Test deleting a terrain."""
        response = client.delete(f"/terrains/{sample_terrain.id}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify it's deleted
        response = client.get(f"/terrains/{sample_terrain.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_terrains_by_user(self, client, sample_user):
        """Test getting terrains filtered by user."""
        # Create multiple terrains for the user
        terrain_data_1 = {
            "name": "Farm 1",
            "description": "First farm",
            "user_id": sample_user.id
        }
        terrain_data_2 = {
            "name": "Farm 2",
            "description": "Second farm",
            "user_id": sample_user.id
        }
        
        client.post("/terrains/", json=terrain_data_1)
        client.post("/terrains/", json=terrain_data_2)
        
        response = client.get(f"/terrains/user/{sample_user.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 2
        assert all(terrain["user_id"] == sample_user.id for terrain in data)
    
    def test_get_terrain_with_parcels(self, client, sample_terrain, sample_parcel):
        """Test getting terrain with its parcels."""
        response = client.get(f"/terrains/{sample_terrain.id}/with-parcels")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == sample_terrain.id
        assert "parcels" in data
        assert len(data["parcels"]) == 1
        assert data["parcels"][0]["id"] == sample_parcel.id
    
    def test_get_terrain_statistics(self, client, sample_terrain, sample_parcel):
        """Test getting terrain statistics."""
        # Create additional parcels
        parcel_data = {
            "name": "Additional Parcel",
            "terrain_id": sample_terrain.id,
            "current_use": "corn",
            "status": "active"
        }
        client.post("/parcels/", json=parcel_data)
        
        response = client.get(f"/terrains/{sample_terrain.id}/statistics")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "total_parcels" in data
        assert data["total_parcels"] == 2
        assert "parcels_by_status" in data
        assert "parcels_by_use" in data
    
    def test_terrain_area_calculation(self, client, sample_terrain):
        """Test terrain area calculation endpoint."""
        response = client.get(f"/terrains/{sample_terrain.id}/area")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "area" in data
        assert "unit" in data
    
    def test_create_terrain_with_geometry(self, client, sample_user):
        """Test creating terrain with geometry data."""
        terrain_data = {
            "name": "Geometric Farm",
            "description": "Farm with defined boundaries",
            "user_id": sample_user.id,
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-73.0, 40.0],
                    [-73.0, 41.0],
                    [-72.0, 41.0],
                    [-72.0, 40.0],
                    [-73.0, 40.0]
                ]]
            }
        }
        
        response = client.post("/terrains/", json=terrain_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Geometric Farm"
        assert "geometry" in data or data["geometry"] is None  # Depends on model configuration
    
    # Test legacy Spanish endpoints
    def test_legacy_get_terrenos(self, client, sample_terrain):
        """Test legacy Spanish endpoint for getting terrains."""
        response = client.get("/terrenos/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_terrain.name
    
    def test_legacy_crear_terreno(self, client, sample_user):
        """Test legacy Spanish endpoint for creating terrain."""
        terrain_data = {
            "name": "Finca Nueva",
            "description": "Nueva finca agrícola",
            "user_id": sample_user.id
        }
        
        response = client.post("/terrenos/", json=terrain_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Finca Nueva"
    
    def test_legacy_obtener_terreno(self, client, sample_terrain):
        """Test legacy Spanish endpoint for getting specific terrain."""
        response = client.get(f"/terrenos/{sample_terrain.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == sample_terrain.id
        assert data["name"] == sample_terrain.name
