"""
Integration tests for complete workflows in AgroVista.
"""
from datetime import date, timedelta

import pytest
from fastapi import status


@pytest.mark.integration
class TestFarmManagementWorkflow:
    """Test complete farm management workflow."""
    
    def test_complete_farm_setup_workflow(self, client):
        """Test setting up a complete farm from scratch."""
        # Step 1: Create a user
        # Note: In real app, this would go through proper user registration
        # user_data would be: {"username": "farmer_john", "email": "john@farm.com", "name": "John Farmer", "hashed_password": "hashed_password"}
        
        # Step 2: Create a terrain
        terrain_data = {
            "name": "Green Valley Farm",
            "description": "200 hectare farm in the valley",
            "user_id": 1  # Assuming user was created
        }
        terrain_response = client.post("/terrains/", json=terrain_data)
        assert terrain_response.status_code == status.HTTP_200_OK
        terrain_id = terrain_response.json()["id"]
        
        # Step 3: Create parcels
        parcels = [
            {"name": "North Field", "current_use": "corn", "status": "active", "terrain_id": terrain_id},
            {"name": "South Field", "current_use": "wheat", "status": "active", "terrain_id": terrain_id},
            {"name": "Greenhouse Area", "current_use": "vegetables", "status": "maintenance", "terrain_id": terrain_id}
        ]
        
        parcel_ids = []
        for parcel in parcels:
            response = client.post("/parcels/", json=parcel)
            assert response.status_code == status.HTTP_200_OK
            parcel_ids.append(response.json()["id"])
        
        # Step 4: Create locations within parcels
        location_data = {
            "name": "Irrigation Point A",
            "description": "Main irrigation system",
            "parcel_id": parcel_ids[0]
        }
        location_response = client.post("/locations/", json=location_data)
        assert location_response.status_code == status.HTTP_200_OK
        location_id = location_response.json()["id"]
        
        # Step 5: Create activities
        activities = [
            {
                "name": "Planting Corn",
                "description": "Plant corn seeds in north field",
                "location_id": location_id,
                "date": str(date.today()),
                "activity_type": "Planting",
                "status": "Completed"
            },
            {
                "name": "Fertilizer Application",
                "description": "Apply NPK fertilizer",
                "location_id": location_id,
                "date": str(date.today() + timedelta(days=7)),
                "activity_type": "Treatment",
                "status": "Planned"
            }
        ]
        
        activity_ids = []
        for activity in activities:
            response = client.post("/activities/", json=activity)
            assert response.status_code == status.HTTP_200_OK
            activity_ids.append(response.json()["id"])
        
        # Step 6: Verify the complete setup
        terrain_response = client.get(f"/terrains/{terrain_id}/with-parcels")
        assert terrain_response.status_code == status.HTTP_200_OK
        terrain_data = terrain_response.json()
        assert len(terrain_data["parcels"]) == 3
        
        # Check activities
        activities_response = client.get(f"/activities/location/{location_id}")
        assert activities_response.status_code == status.HTTP_200_OK
        assert len(activities_response.json()) == 2


@pytest.mark.integration
class TestInventoryManagementWorkflow:
    """Test complete inventory management workflow."""
    
    def test_inventory_tracking_workflow(self, client, sample_user):
        """Test complete inventory tracking from purchase to usage."""
        # Step 1: Create inventory items
        items = [
            {
                "name": "NPK Fertilizer 20-20-20",
                "description": "Balanced fertilizer",
                "unit": "kg",
                "stock": 0,
                "min_stock": 100,
                "user_id": sample_user.id
            },
            {
                "name": "Corn Seeds",
                "description": "Hybrid variety",
                "unit": "kg",
                "stock": 0,
                "min_stock": 50,
                "user_id": sample_user.id
            }
        ]
        
        item_ids = []
        for item in items:
            response = client.post("/inventory/items/", json=item)
            assert response.status_code == status.HTTP_200_OK
            item_ids.append(response.json()["id"])
        
        # Step 2: Record purchases (inventory entries)
        purchases = [
            {
                "inventory_id": item_ids[0],
                "event_type": "Entry",
                "quantity": 500,
                "unit_price": 2.5,
                "observations": "Purchased from AgriSupply Co."
            },
            {
                "inventory_id": item_ids[1],
                "event_type": "Entry",
                "quantity": 100,
                "unit_price": 15.0,
                "observations": "Premium seeds"
            }
        ]
        
        for purchase in purchases:
            response = client.post("/inventory/events/", json=purchase)
            assert response.status_code == status.HTTP_200_OK
        
        # Step 3: Check updated stock levels
        response = client.get(f"/inventory/items/{item_ids[0]}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["stock"] == 500
        
        # Step 4: Use inventory (exits)
        usage_events = [
            {
                "inventory_id": item_ids[0],
                "event_type": "Exit",
                "quantity": -150,
                "unit_price": 2.5,
                "observations": "Used in north field"
            },
            {
                "inventory_id": item_ids[1],
                "event_type": "Exit",
                "quantity": -30,
                "unit_price": 15.0,
                "observations": "Planted in section A"
            }
        ]
        
        for usage in usage_events:
            response = client.post("/inventory/events/", json=usage)
            assert response.status_code == status.HTTP_200_OK
        
        # Step 5: Check low stock alerts
        response = client.get("/inventory/low-stock/")
        assert response.status_code == status.HTTP_200_OK
        low_stock_items = response.json()
        # Seeds should be below minimum (70 < 50 min)
        assert any(item["name"] == "Corn Seeds" for item in low_stock_items)
        
        # Step 6: Generate inventory report
        response = client.get(f"/inventory/movements-report/{item_ids[0]}")
        assert response.status_code == status.HTTP_200_OK
        report = response.json()
        assert report["total_entries"] == 500
        assert report["total_exits"] == -150
        assert report["current_stock"] == 350


@pytest.mark.integration
class TestFinancialManagementWorkflow:
    """Test complete financial management workflow."""
    
    def test_financial_tracking_workflow(self, client, sample_parcel, sample_user):
        """Test complete financial tracking from budget to analysis."""
        # Step 1: Create annual budget
        budget_data = {
            "name": "2024 Annual Budget",
            "amount": 50000,
            "budget_type": "Annual",
            "period": "2024",
            "parcel_id": sample_parcel.id,
            "user_id": sample_user.id
        }
        
        budget_response = client.post("/economy/budgets/", json=budget_data)
        assert budget_response.status_code == status.HTTP_200_OK
        budget_id = budget_response.json()["id"]
        
        # Step 2: Record transactions throughout the year
        transactions = [
            # Income
            {"name": "Corn Sale Q1", "transaction_type": "Income", "category": "Sales", 
             "amount": 15000, "date": "2024-03-15", "parcel_id": sample_parcel.id},
            {"name": "Wheat Sale Q2", "transaction_type": "Income", "category": "Sales", 
             "amount": 12000, "date": "2024-06-20", "parcel_id": sample_parcel.id},
            
            # Expenses
            {"name": "Seeds Purchase", "transaction_type": "Expense", "category": "Purchases", 
             "amount": 3000, "date": "2024-02-01", "parcel_id": sample_parcel.id},
            {"name": "Fertilizer", "transaction_type": "Expense", "category": "Purchases", 
             "amount": 5000, "date": "2024-02-15", "parcel_id": sample_parcel.id},
            {"name": "Labor Q1", "transaction_type": "Expense", "category": "Labor", 
             "amount": 8000, "date": "2024-03-30", "parcel_id": sample_parcel.id},
            {"name": "Equipment Maintenance", "transaction_type": "Expense", "category": "Other", 
             "amount": 2000, "date": "2024-05-10", "parcel_id": sample_parcel.id}
        ]
        
        for trans in transactions:
            response = client.post("/economy/transactions/", json=trans)
            assert response.status_code == status.HTTP_200_OK
        
        # Step 3: Check financial summary
        response = client.get("/economy/summary/")
        assert response.status_code == status.HTTP_200_OK
        summary = response.json()
        assert summary["total_income"] == 27000
        assert summary["total_expenses"] == 18000
        assert summary["net_balance"] == 9000
        
        # Step 4: Check monthly breakdown
        response = client.get("/economy/summary/monthly/2024")
        assert response.status_code == status.HTTP_200_OK
        monthly_data = response.json()
        
        # Find March data
        march_data = next((m for m in monthly_data if m["month"] == 3), None)
        assert march_data is not None
        assert march_data["income"] == 15000
        assert march_data["expenses"] == 8000
        
        # Step 5: Check budget vs actual
        response = client.get(f"/economy/budgets/{budget_id}/vs-actual")
        assert response.status_code == status.HTTP_200_OK
        budget_analysis = response.json()
        assert budget_analysis["budget_amount"] == 50000
        assert budget_analysis["actual_amount"] == 18000  # Total expenses
        assert budget_analysis["percentage_used"] == 36.0
        
        # Step 6: Generate cash flow report
        response = client.get("/economy/cash-flow/2024-01-01/2024-12-31")
        assert response.status_code == status.HTTP_200_OK
        cash_flow = response.json()
        assert "daily_flow" in cash_flow
        assert "cumulative_balance" in cash_flow


@pytest.mark.integration
class TestSimulationWorkflow:
    """Test simulation and analysis workflow."""
    
    def test_crop_simulation_workflow(self, client, sample_parcel):
        """Test complete crop growth simulation workflow."""
        # Step 1: Set up biological parameters
        bio_params = [
            {
                "name": "Corn Growth Rate",
                "value": 2.5,
                "unit": "cm/day",
                "date": str(date.today()),
                "parcel_id": sample_parcel.id
            },
            {
                "name": "Water Requirement",
                "value": 500,
                "unit": "mm/season",
                "date": str(date.today()),
                "parcel_id": sample_parcel.id
            }
        ]
        
        for param in bio_params:
            response = client.post("/biological-parameters/", json=param)
            assert response.status_code == status.HTTP_200_OK
        
        # Step 2: Create simulation scenarios
        scenarios = [
            {
                "name": "Normal Weather Scenario",
                "description": "Average temperature and rainfall",
                "parcel_id": sample_parcel.id,
                "parameters": {
                    "temperature_avg": 25,
                    "rainfall_total": 600,
                    "growth_days": 120,
                    "fertilizer_amount": 150
                }
            },
            {
                "name": "Drought Scenario",
                "description": "Low rainfall conditions",
                "parcel_id": sample_parcel.id,
                "parameters": {
                    "temperature_avg": 28,
                    "rainfall_total": 300,
                    "growth_days": 120,
                    "fertilizer_amount": 150
                }
            }
        ]
        
        simulation_ids = []
        for scenario in scenarios:
            response = client.post("/simulation/create", json=scenario)
            assert response.status_code == status.HTTP_200_OK
            simulation_ids.append(response.json()["id"])
        
        # Step 3: Run simulations
        for sim_id in simulation_ids:
            response = client.post(f"/simulation/run/{sim_id}")
            assert response.status_code == status.HTTP_200_OK
        
        # Step 4: Compare results
        response = client.post("/simulation/compare", 
                             json={"simulation_ids": simulation_ids})
        assert response.status_code == status.HTTP_200_OK
        comparison = response.json()
        assert len(comparison["comparison"]) == 2
        
        # Step 5: Create indicators based on results
        indicator_data = {
            "name": "Projected Yield",
            "value": 4500,
            "unit": "kg/ha",
            "date": str(date.today()),
            "parcel_id": sample_parcel.id,
            "description": "Based on normal weather simulation"
        }
        
        response = client.post("/indicators/", json=indicator_data)
        assert response.status_code == status.HTTP_200_OK
