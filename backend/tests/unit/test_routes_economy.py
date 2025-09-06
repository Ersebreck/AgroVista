"""
Unit tests for economy routes.
"""
from fastapi import status


class TestEconomyRoutes:
    """Test economy-related API endpoints."""
    
    def test_get_transactions_empty(self, client):
        """Test getting transactions when none exist."""
        response = client.get("/economy/transactions/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_create_transaction(self, client, sample_parcel, sample_activity):
        """Test creating a new transaction."""
        transaction_data = {
            "name": "Fertilizer Purchase",
            "transaction_type": "Expense",
            "category": "Purchases",
            "amount": 500.0,
            "date": "2024-07-01",
            "description": "NPK fertilizer for corn field",
            "parcel_id": sample_parcel.id,
            "activity_id": sample_activity.id
        }
        
        response = client.post("/economy/transactions/", json=transaction_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Fertilizer Purchase"
        assert data["transaction_type"] == "Expense"
        assert data["amount"] == 500.0
        assert "id" in data
    
    def test_get_transactions_with_filters(self, client, sample_parcel):
        """Test getting transactions with filters."""
        # Create transactions
        transactions = [
            {
                "name": "Seed Purchase",
                "transaction_type": "Expense",
                "category": "Purchases",
                "amount": 200.0,
                "date": "2024-06-01",
                "parcel_id": sample_parcel.id
            },
            {
                "name": "Crop Sale",
                "transaction_type": "Income",
                "category": "Sales",
                "amount": 1500.0,
                "date": "2024-07-15",
                "parcel_id": sample_parcel.id
            }
        ]
        
        for trans in transactions:
            client.post("/economy/transactions/", json=trans)
        
        # Test filter by type
        response = client.get("/economy/transactions/?transaction_type=Income")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Crop Sale"
        
        # Test filter by parcel
        response = client.get(f"/economy/transactions/?parcel_id={sample_parcel.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
    
    def test_get_transaction_by_id(self, client, sample_parcel):
        """Test getting a specific transaction by ID."""
        # Create transaction
        transaction_data = {
            "name": "Labor Cost",
            "transaction_type": "Expense",
            "category": "Labor",
            "amount": 300.0,
            "date": "2024-07-01",
            "parcel_id": sample_parcel.id
        }
        
        create_response = client.post("/economy/transactions/", json=transaction_data)
        transaction_id = create_response.json()["id"]
        
        response = client.get(f"/economy/transactions/{transaction_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == transaction_id
        assert data["name"] == "Labor Cost"
    
    def test_update_transaction(self, client, sample_parcel):
        """Test updating a transaction."""
        # Create transaction
        transaction_data = {
            "name": "Initial Cost",
            "transaction_type": "Expense",
            "category": "Other",
            "amount": 100.0,
            "date": "2024-07-01",
            "parcel_id": sample_parcel.id
        }
        
        create_response = client.post("/economy/transactions/", json=transaction_data)
        transaction_id = create_response.json()["id"]
        
        # Update transaction
        update_data = {
            "name": "Updated Cost",
            "amount": 150.0
        }
        
        response = client.put(f"/economy/transactions/{transaction_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Updated Cost"
        assert data["amount"] == 150.0
    
    def test_delete_transaction(self, client, sample_parcel):
        """Test deleting a transaction."""
        # Create transaction
        transaction_data = {
            "name": "To Delete",
            "transaction_type": "Expense",
            "category": "Other",
            "amount": 50.0,
            "date": "2024-07-01",
            "parcel_id": sample_parcel.id
        }
        
        create_response = client.post("/economy/transactions/", json=transaction_data)
        transaction_id = create_response.json()["id"]
        
        # Delete transaction
        response = client.delete(f"/economy/transactions/{transaction_id}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify it's deleted
        response = client.get(f"/economy/transactions/{transaction_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_financial_summary(self, client, sample_parcel):
        """Test getting financial summary."""
        # Create transactions
        transactions = [
            {"name": "Income 1", "transaction_type": "Income", "category": "Sales", "amount": 1000.0, "date": "2024-07-01", "parcel_id": sample_parcel.id},
            {"name": "Income 2", "transaction_type": "Income", "category": "Sales", "amount": 500.0, "date": "2024-07-02", "parcel_id": sample_parcel.id},
            {"name": "Expense 1", "transaction_type": "Expense", "category": "Purchases", "amount": 300.0, "date": "2024-07-01", "parcel_id": sample_parcel.id},
            {"name": "Expense 2", "transaction_type": "Expense", "category": "Labor", "amount": 200.0, "date": "2024-07-02", "parcel_id": sample_parcel.id}
        ]
        
        for trans in transactions:
            client.post("/economy/transactions/", json=trans)
        
        response = client.get("/economy/summary/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["total_income"] == 1500.0
        assert data["total_expenses"] == 500.0
        assert data["net_balance"] == 1000.0
    
    def test_get_monthly_summary(self, client, sample_parcel):
        """Test getting monthly financial summary."""
        # Create transactions for different months
        transactions = [
            {"name": "July Income", "transaction_type": "Income", "category": "Sales", "amount": 1000.0, "date": "2024-07-15", "parcel_id": sample_parcel.id},
            {"name": "July Expense", "transaction_type": "Expense", "category": "Purchases", "amount": 400.0, "date": "2024-07-20", "parcel_id": sample_parcel.id},
            {"name": "June Income", "transaction_type": "Income", "category": "Sales", "amount": 800.0, "date": "2024-06-15", "parcel_id": sample_parcel.id}
        ]
        
        for trans in transactions:
            client.post("/economy/transactions/", json=trans)
        
        response = client.get("/economy/summary/monthly/2024")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        
        # Find July summary
        july_summary = next((item for item in data if item["month"] == 7), None)
        assert july_summary is not None
        assert july_summary["income"] == 1000.0
        assert july_summary["expenses"] == 400.0
        assert july_summary["net"] == 600.0
    
    def test_create_budget(self, client, sample_parcel, sample_user):
        """Test creating a budget."""
        budget_data = {
            "name": "Annual Budget 2024",
            "amount": 10000.0,
            "budget_type": "Annual",
            "period": "2024",
            "parcel_id": sample_parcel.id,
            "user_id": sample_user.id
        }
        
        response = client.post("/economy/budgets/", json=budget_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Annual Budget 2024"
        assert data["amount"] == 10000.0
        assert "id" in data
    
    def test_get_budgets(self, client, sample_parcel, sample_user):
        """Test getting budgets."""
        # Create budget
        budget_data = {
            "name": "Q1 Budget",
            "amount": 2500.0,
            "budget_type": "Quarterly",
            "period": "2024-Q1",
            "parcel_id": sample_parcel.id,
            "user_id": sample_user.id
        }
        
        client.post("/economy/budgets/", json=budget_data)
        
        response = client.get("/economy/budgets/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Q1 Budget"
    
    def test_get_budget_vs_actual(self, client, sample_parcel, sample_user):
        """Test budget vs actual comparison."""
        # Create budget
        budget_data = {
            "name": "Monthly Budget",
            "amount": 1000.0,
            "budget_type": "Monthly",
            "period": "2024-07",
            "parcel_id": sample_parcel.id,
            "user_id": sample_user.id
        }
        
        budget_response = client.post("/economy/budgets/", json=budget_data)
        budget_id = budget_response.json()["id"]
        
        # Create transactions
        transactions = [
            {"name": "Expense 1", "transaction_type": "Expense", "category": "Purchases", "amount": 400.0, "date": "2024-07-10", "parcel_id": sample_parcel.id},
            {"name": "Expense 2", "transaction_type": "Expense", "category": "Labor", "amount": 300.0, "date": "2024-07-20", "parcel_id": sample_parcel.id}
        ]
        
        for trans in transactions:
            client.post("/economy/transactions/", json=trans)
        
        response = client.get(f"/economy/budgets/{budget_id}/vs-actual")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["budget_amount"] == 1000.0
        assert data["actual_amount"] == 700.0
        assert data["variance"] == 300.0
        assert data["percentage_used"] == 70.0
    
    def test_get_cash_flow(self, client, sample_parcel):
        """Test getting cash flow report."""
        # Create transactions
        transactions = [
            {"name": "Income 1", "transaction_type": "Income", "category": "Sales", "amount": 2000.0, "date": "2024-07-01", "parcel_id": sample_parcel.id},
            {"name": "Expense 1", "transaction_type": "Expense", "category": "Purchases", "amount": 500.0, "date": "2024-07-05", "parcel_id": sample_parcel.id},
            {"name": "Income 2", "transaction_type": "Income", "category": "Sales", "amount": 1000.0, "date": "2024-07-10", "parcel_id": sample_parcel.id},
            {"name": "Expense 2", "transaction_type": "Expense", "category": "Labor", "amount": 700.0, "date": "2024-07-15", "parcel_id": sample_parcel.id}
        ]
        
        for trans in transactions:
            client.post("/economy/transactions/", json=trans)
        
        response = client.get("/economy/cash-flow/2024-07-01/2024-07-31")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "daily_flow" in data
        assert "cumulative_balance" in data
        assert len(data["daily_flow"]) > 0
    
    # Test legacy Spanish endpoints
    def test_legacy_get_transacciones(self, client):
        """Test legacy Spanish endpoint for getting transactions."""
        response = client.get("/economia/transacciones/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
