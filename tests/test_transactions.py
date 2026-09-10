def test_create_transaction(client, auth_headers):
    """
    Test Case 1: Create transaction test
    - Automatically assigns logged-in user as owner
    - Validates amount must be positive and type must be income/expense
    """
    # Valid transaction creation
    payload = {
        "title": "Salary",
        "amount": 5000.0,
        "type": "income",
        "category": "Job",
        "date": "2026-09-10",
    }
    response = client.post("/transactions", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Salary"
    assert data["amount"] == 5000.0
    assert data["type"] == "income"
    assert data["category"] == "Job"
    assert data["date"] == "2026-09-10"
    assert "id" in data
    assert "owner_id" in data

    # Validation: amount must be positive (> 0)
    invalid_amount_payload = {
        "title": "Zero Amount",
        "amount": -10.0,
        "type": "expense",
        "category": "Misc",
        "date": "2026-09-10",
    }
    resp_invalid_amount = client.post("/transactions", json=invalid_amount_payload, headers=auth_headers)
    assert resp_invalid_amount.status_code == 422

    # Validation: type must be either 'income' or 'expense'
    invalid_type_payload = {
        "title": "Invalid Type",
        "amount": 100.0,
        "type": "invalid_type",
        "category": "Misc",
        "date": "2026-09-10",
    }
    resp_invalid_type = client.post("/transactions", json=invalid_type_payload, headers=auth_headers)
    assert resp_invalid_type.status_code == 422


def test_get_all_transactions(client, auth_headers, second_user_auth_headers):
    """
    Test Case 2: Get all transactions test
    - Returns all transactions belonging to logged-in user only
    """
    # Create transactions for user 1
    t1 = {
        "title": "Groceries",
        "amount": 150.0,
        "type": "expense",
        "category": "Food",
        "date": "2026-09-10",
    }
    t2 = {
        "title": "Freelance",
        "amount": 800.0,
        "type": "income",
        "category": "Work",
        "date": "2026-09-10",
    }
    client.post("/transactions", json=t1, headers=auth_headers)
    client.post("/transactions", json=t2, headers=auth_headers)

    # Create transaction for user 2 (should not appear in user 1's list)
    t_other = {
        "title": "Other User Expense",
        "amount": 300.0,
        "type": "expense",
        "category": "Travel",
        "date": "2026-09-10",
    }
    client.post("/transactions", json=t_other, headers=second_user_auth_headers)

    # Get all transactions for user 1
    response = client.get("/transactions", headers=auth_headers)
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 2
    titles = [t["title"] for t in transactions]
    assert "Groceries" in titles
    assert "Freelance" in titles
    assert "Other User Expense" not in titles


def test_get_specific_transaction(client, auth_headers, second_user_auth_headers):
    """
    Test Case 3: Get specific transaction test
    - Returns the specific transaction by ID
    - Returns 404 if transaction does not exist
    - Ensures a user cannot access another user's transaction
    """
    # Create transaction for user 1
    payload = {
        "title": "Electricity Bill",
        "amount": 120.0,
        "type": "expense",
        "category": "Utilities",
        "date": "2026-09-10",
    }
    create_resp = client.post("/transactions", json=payload, headers=auth_headers)
    tx_id = create_resp.json()["id"]

    # Successfully get existing transaction
    response = client.get(f"/transactions/{tx_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Electricity Bill"
    assert response.json()["amount"] == 120.0

    # Non-existent transaction returns 404
    non_existent = client.get("/transactions/99999", headers=auth_headers)
    assert non_existent.status_code == 404
    assert non_existent.json()["detail"] == "Transaction not found"

    # User 2 cannot access user 1's transaction
    unauthorized_get = client.get(f"/transactions/{tx_id}", headers=second_user_auth_headers)
    assert unauthorized_get.status_code == 404
    assert unauthorized_get.json()["detail"] == "Transaction not found"


def test_update_transaction(client, auth_headers, second_user_auth_headers):
    """
    Test Case 4: Update transaction test
    - Updates only the user's own transaction
    - Returns updated transaction
    - Returns 404 if transaction does not exist or belongs to another user
    """
    # Create transaction
    payload = {
        "title": "Internet",
        "amount": 60.0,
        "type": "expense",
        "category": "Utilities",
        "date": "2026-09-10",
    }
    create_resp = client.post("/transactions", json=payload, headers=auth_headers)
    tx_id = create_resp.json()["id"]

    # Update transaction
    update_payload = {
        "title": "Internet Fiber",
        "amount": 75.0,
    }
    update_resp = client.put(f"/transactions/{tx_id}", json=update_payload, headers=auth_headers)
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["title"] == "Internet Fiber"
    assert updated_data["amount"] == 75.0
    assert updated_data["type"] == "expense"  # preserved

    # Non-existent transaction returns 404
    non_existent = client.put("/transactions/99999", json=update_payload, headers=auth_headers)
    assert non_existent.status_code == 404

    # User 2 cannot update user 1's transaction
    unauthorized_update = client.put(f"/transactions/{tx_id}", json=update_payload, headers=second_user_auth_headers)
    assert unauthorized_update.status_code == 404


def test_delete_transaction(client, auth_headers, second_user_auth_headers):
    """
    Test Case 5: Delete transaction test
    - Deletes matching row from database
    - Returns confirmation message with status 200
    - Returns 404 if not found
    - Cannot delete another user's transaction
    """
    # Create transaction
    payload = {
        "title": "Coffee",
        "amount": 5.0,
        "type": "expense",
        "category": "Food",
        "date": "2026-09-10",
    }
    create_resp = client.post("/transactions", json=payload, headers=auth_headers)
    tx_id = create_resp.json()["id"]

    # User 2 cannot delete user 1's transaction
    unauthorized_del = client.delete(f"/transactions/{tx_id}", headers=second_user_auth_headers)
    assert unauthorized_del.status_code == 404

    # Successfully delete transaction
    del_resp = client.delete(f"/transactions/{tx_id}", headers=auth_headers)
    assert del_resp.status_code == 200
    assert del_resp.json() == {"message": "Transaction deleted successfully"}

    # Verifying it was deleted (subsequent GET returns 404)
    get_resp = client.get(f"/transactions/{tx_id}", headers=auth_headers)
    assert get_resp.status_code == 404

    # Deleting again returns 404
    del_again = client.delete(f"/transactions/{tx_id}", headers=auth_headers)
    assert del_again.status_code == 404


def test_filter_transactions(client, auth_headers):
    """
    Test Transaction Filtering:
    - Filters by type, category, minimum_amount, maximum_amount
    """
    client.post("/transactions", json={
        "title": "Lunch",
        "amount": 25.0,
        "type": "expense",
        "category": "Food",
        "date": "2026-09-10",
    }, headers=auth_headers)

    client.post("/transactions", json={
        "title": "Dinner Buffet",
        "amount": 120.0,
        "type": "expense",
        "category": "Food",
        "date": "2026-09-10",
    }, headers=auth_headers)

    client.post("/transactions", json={
        "title": "Tech Stipend",
        "amount": 500.0,
        "type": "income",
        "category": "Salary",
        "date": "2026-09-10",
    }, headers=auth_headers)

    # Filter by category Food and type expense
    resp = client.get("/transactions/filter?type=expense&category=Food", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert all(item["category"] == "Food" and item["type"] == "expense" for item in data)

    # Filter by minimum amount
    resp_min = client.get("/transactions/filter?minimum_amount=100", headers=auth_headers)
    assert resp_min.status_code == 200
    data_min = resp_min.json()
    assert len(data_min) == 2
    assert all(item["amount"] >= 100 for item in data_min)

    # Filter by amount range
    resp_range = client.get("/transactions/filter?minimum_amount=20&maximum_amount=50", headers=auth_headers)
    assert resp_range.status_code == 200
    data_range = resp_range.json()
    assert len(data_range) == 1
    assert data_range[0]["title"] == "Lunch"
