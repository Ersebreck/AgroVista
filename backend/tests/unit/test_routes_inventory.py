"""
Unit tests for inventory routes.
"""
from fastapi import status


class TestInventoryRoutes:
    """Test inventory-related API endpoints."""
    
    def test_get_inventory_items_empty(self, client):
        """Test getting inventory items when none exist."""
        response = client.get("/inventory/items/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_create_inventory_item(self, client, sample_user):
        """Test creating a new inventory item."""
        item_data = {
            "name": "NPK Fertilizer",
            "description": "20-20-20 Formula",
            "unit": "kg",
            "stock": 500.0,
            "min_stock": 50.0,
            "user_id": sample_user.id
        }
        
        response = client.post("/inventory/items/", json=item_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "NPK Fertilizer"
        assert data["stock"] == 500.0
        assert data["min_stock"] == 50.0
        assert "id" in data
    
    def test_get_inventory_items_with_data(self, client, sample_inventory):
        """Test getting inventory items when data exists."""
        response = client.get("/inventory/items/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_inventory.name
    
    def test_get_inventory_item_by_id(self, client, sample_inventory):
        """Test getting a specific inventory item by ID."""
        response = client.get(f"/inventory/items/{sample_inventory.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == sample_inventory.id
        assert data["name"] == sample_inventory.name
    
    def test_update_inventory_item(self, client, sample_inventory):
        """Test updating an inventory item."""
        update_data = {
            "name": "Updated Fertilizer",
            "stock": 600.0
        }
        
        response = client.put(f"/inventory/items/{sample_inventory.id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Updated Fertilizer"
        assert data["stock"] == 600.0
    
    def test_delete_inventory_item(self, client, sample_inventory):
        """Test deleting an inventory item."""
        response = client.delete(f"/inventory/items/{sample_inventory.id}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify it's deleted
        response = client.get(f"/inventory/items/{sample_inventory.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_inventory_event(self, client, sample_inventory):
        """Test creating an inventory event."""
        event_data = {
            "inventory_id": sample_inventory.id,
            "event_type": "Entry",
            "quantity": 100.0,
            "unit_price": 10.0,
            "observations": "Purchase from supplier"
        }
        
        response = client.post("/inventory/events/", json=event_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["inventory_id"] == sample_inventory.id
        assert data["event_type"] == "Entry"
        assert data["quantity"] == 100.0
    
    def test_get_inventory_events(self, client, sample_inventory):
        """Test getting inventory events."""
        # Create an event first
        event_data = {
            "inventory_id": sample_inventory.id,
            "event_type": "Exit",
            "quantity": -50.0,
            "unit_price": 12.0
        }
        client.post("/inventory/events/", json=event_data)
        
        # Get events
        response = client.get(f"/inventory/events/?inventory_id={sample_inventory.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["event_type"] == "Exit"
    
    def test_get_low_stock_items(self, client, sample_user):
        """Test getting low stock items."""
        # Create items with different stock levels
        item1_data = {
            "name": "Low Stock Item",
            "unit": "units",
            "stock": 5.0,
            "min_stock": 10.0,
            "user_id": sample_user.id
        }
        item2_data = {
            "name": "High Stock Item",
            "unit": "units",
            "stock": 100.0,
            "min_stock": 10.0,
            "user_id": sample_user.id
        }
        
        client.post("/inventory/items/", json=item1_data)
        client.post("/inventory/items/", json=item2_data)
        
        # Get low stock items
        response = client.get("/inventory/low-stock/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Low Stock Item"
    
    def test_get_inventory_value(self, client, sample_inventory):
        """Test getting total inventory value."""
        # Create events to establish value
        event_data = {
            "inventory_id": sample_inventory.id,
            "event_type": "Entry",
            "quantity": 100.0,
            "unit_price": 15.0
        }
        client.post("/inventory/events/", json=event_data)
        
        response = client.get("/inventory/value/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "total_value" in data
        assert data["total_value"] > 0
    
    def test_get_inventory_movements_report(self, client, sample_inventory):
        """Test getting inventory movements report."""
        # Create some events
        events = [
            {"inventory_id": sample_inventory.id, "event_type": "Entry", "quantity": 100.0, "unit_price": 10.0},
            {"inventory_id": sample_inventory.id, "event_type": "Exit", "quantity": -30.0, "unit_price": 12.0},
            {"inventory_id": sample_inventory.id, "event_type": "Adjustment", "quantity": -5.0, "unit_price": 0.0}
        ]
        
        for event in events:
            client.post("/inventory/events/", json=event)
        
        response = client.get(f"/inventory/movements-report/{sample_inventory.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "item_name" in data
        assert "total_entries" in data
        assert "total_exits" in data
        assert "total_adjustments" in data
        assert data["total_entries"] == 100.0
        assert data["total_exits"] == -30.0
        assert data["total_adjustments"] == -5.0
    
    # Test legacy Spanish endpoints
    def test_legacy_get_inventario(self, client, sample_inventory):
        """Test legacy Spanish endpoint for getting inventory."""
        response = client.get("/inventario/items/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_inventory.name
    
    def test_legacy_crear_item_inventario(self, client, sample_user):
        """Test legacy Spanish endpoint for creating inventory item."""
        item_data = {
            "name": "Semillas de Maíz",
            "description": "Variedad resistente",
            "unit": "kg",
            "stock": 200.0,
            "min_stock": 20.0,
            "user_id": sample_user.id
        }
        
        response = client.post("/inventario/items/", json=item_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Semillas de Maíz"
