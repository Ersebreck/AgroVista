"""
Unit tests for simulation routes.
"""
from fastapi import status


class TestSimulationRoutes:
    """Test simulation-related API endpoints."""
    
    def test_create_simulation(self, client, sample_parcel):
        """Test creating a new simulation."""
        simulation_data = {
            "name": "Crop Yield Simulation",
            "description": "Simulating corn yield for next season",
            "parcel_id": sample_parcel.id,
            "parameters": {
                "temperature": 25,
                "rainfall": 800,
                "fertilizer": 150,
                "seed_variety": "hybrid"
            }
        }
        
        response = client.post("/simulation/create", json=simulation_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Crop Yield Simulation"
        assert "id" in data
        assert "created_at" in data
    
    def test_run_simulation(self, client, sample_parcel):
        """Test running a simulation."""
        # Create simulation first
        simulation_data = {
            "name": "Growth Simulation",
            "description": "Simulate plant growth",
            "parcel_id": sample_parcel.id,
            "parameters": {
                "days": 90,
                "initial_height": 10,
                "growth_rate": 0.5
            }
        }
        
        create_response = client.post("/simulation/create", json=simulation_data)
        simulation_id = create_response.json()["id"]
        
        # Run simulation
        response = client.post(f"/simulation/run/{simulation_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "results" in data
        assert data["results"] is not None
    
    def test_get_simulations(self, client, sample_parcel):
        """Test getting list of simulations."""
        # Create multiple simulations
        simulations = [
            {
                "name": "Simulation 1",
                "parcel_id": sample_parcel.id,
                "parameters": {"test": 1}
            },
            {
                "name": "Simulation 2",
                "parcel_id": sample_parcel.id,
                "parameters": {"test": 2}
            }
        ]
        
        for sim in simulations:
            client.post("/simulation/create", json=sim)
        
        response = client.get("/simulation/list")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) >= 2
        assert any(sim["name"] == "Simulation 1" for sim in data)
        assert any(sim["name"] == "Simulation 2" for sim in data)
    
    def test_get_simulation_by_id(self, client, sample_parcel):
        """Test getting a specific simulation."""
        # Create simulation
        simulation_data = {
            "name": "Test Simulation",
            "description": "Test description",
            "parcel_id": sample_parcel.id,
            "parameters": {"param1": "value1"}
        }
        
        create_response = client.post("/simulation/create", json=simulation_data)
        simulation_id = create_response.json()["id"]
        
        response = client.get(f"/simulation/{simulation_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == simulation_id
        assert data["name"] == "Test Simulation"
        assert data["parameters"]["param1"] == "value1"
    
    def test_update_simulation_parameters(self, client, sample_parcel):
        """Test updating simulation parameters."""
        # Create simulation
        simulation_data = {
            "name": "Parameter Test",
            "parcel_id": sample_parcel.id,
            "parameters": {"old_param": "old_value"}
        }
        
        create_response = client.post("/simulation/create", json=simulation_data)
        simulation_id = create_response.json()["id"]
        
        # Update parameters
        new_parameters = {
            "new_param": "new_value",
            "another_param": 123
        }
        
        response = client.put(f"/simulation/{simulation_id}/parameters", json=new_parameters)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["parameters"]["new_param"] == "new_value"
        assert data["parameters"]["another_param"] == 123
    
    def test_delete_simulation(self, client, sample_parcel):
        """Test deleting a simulation."""
        # Create simulation
        simulation_data = {
            "name": "To Delete",
            "parcel_id": sample_parcel.id,
            "parameters": {}
        }
        
        create_response = client.post("/simulation/create", json=simulation_data)
        simulation_id = create_response.json()["id"]
        
        # Delete simulation
        response = client.delete(f"/simulation/{simulation_id}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify it's deleted
        response = client.get(f"/simulation/{simulation_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_simulation_results(self, client, sample_parcel):
        """Test getting simulation results."""
        # Create and run simulation
        simulation_data = {
            "name": "Results Test",
            "parcel_id": sample_parcel.id,
            "parameters": {
                "duration": 30,
                "intensity": "high"
            }
        }
        
        create_response = client.post("/simulation/create", json=simulation_data)
        simulation_id = create_response.json()["id"]
        
        # Run simulation
        client.post(f"/simulation/run/{simulation_id}")
        
        # Get results
        response = client.get(f"/simulation/{simulation_id}/results")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], dict)
    
    def test_compare_simulations(self, client, sample_parcel):
        """Test comparing multiple simulations."""
        # Create simulations
        sim1_data = {
            "name": "Scenario A",
            "parcel_id": sample_parcel.id,
            "parameters": {"scenario": "A"}
        }
        sim2_data = {
            "name": "Scenario B",
            "parcel_id": sample_parcel.id,
            "parameters": {"scenario": "B"}
        }
        
        sim1_response = client.post("/simulation/create", json=sim1_data)
        sim2_response = client.post("/simulation/create", json=sim2_data)
        
        sim1_id = sim1_response.json()["id"]
        sim2_id = sim2_response.json()["id"]
        
        # Run both simulations
        client.post(f"/simulation/run/{sim1_id}")
        client.post(f"/simulation/run/{sim2_id}")
        
        # Compare simulations
        response = client.post("/simulation/compare", json={"simulation_ids": [sim1_id, sim2_id]})
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "comparison" in data
        assert len(data["comparison"]) == 2
    
    def test_export_simulation_data(self, client, sample_parcel):
        """Test exporting simulation data."""
        # Create and run simulation
        simulation_data = {
            "name": "Export Test",
            "parcel_id": sample_parcel.id,
            "parameters": {"export": True}
        }
        
        create_response = client.post("/simulation/create", json=simulation_data)
        simulation_id = create_response.json()["id"]
        
        client.post(f"/simulation/run/{simulation_id}")
        
        # Export data
        response = client.get(f"/simulation/{simulation_id}/export")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "name" in data
        assert "parameters" in data
        assert "results" in data
        assert "created_at" in data
    
    def test_get_simulation_history(self, client, sample_parcel):
        """Test getting simulation history for a parcel."""
        # Create multiple simulations for the parcel
        for i in range(3):
            sim_data = {
                "name": f"History Test {i}",
                "parcel_id": sample_parcel.id,
                "parameters": {"iteration": i}
            }
            client.post("/simulation/create", json=sim_data)
        
        response = client.get(f"/simulation/history/parcel/{sample_parcel.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) >= 3
        assert all(sim["parcel_id"] == sample_parcel.id for sim in data)
    
    # Test legacy Spanish endpoints
    def test_legacy_crear_simulacion(self, client, sample_parcel):
        """Test legacy Spanish endpoint for creating simulation."""
        simulation_data = {
            "name": "Simulación de Rendimiento",
            "description": "Simulando rendimiento de maíz",
            "parcel_id": sample_parcel.id,
            "parameters": {
                "temperatura": 25,
                "lluvia": 800
            }
        }
        
        response = client.post("/simulacion/crear", json=simulation_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Simulación de Rendimiento"
    
    def test_legacy_ejecutar_simulacion(self, client, sample_parcel):
        """Test legacy Spanish endpoint for running simulation."""
        # Create simulation first
        simulation_data = {
            "name": "Test Simulación",
            "parcel_id": sample_parcel.id,
            "parameters": {}
        }
        
        create_response = client.post("/simulacion/crear", json=simulation_data)
        simulation_id = create_response.json()["id"]
        
        # Run simulation
        response = client.post(f"/simulacion/ejecutar/{simulation_id}")
        assert response.status_code == status.HTTP_200_OK
