import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.main import app
from src.api.database import Base, get_db
from src.api import models

# Use a separate test database to avoid polluting production data
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/cloud_devops_test_db"
)

# Create test engine and session
engine = create_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# Override the get_db dependency for testing
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Pytest fixture for database setup/teardown
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_product(client, db_session):
    product_data = {
        "name": "Test Product",
        "description": "A product for testing.",
        "price": 19.99
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["description"] == product_data["description"]
    assert float(data["price"]) == product_data["price"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_duplicate_product(client):
    product_data = {
        "name": "Duplicate Product",
        "description": "First instance.",
        "price": 10.00
    }
    # First creation should succeed
    response1 = client.post("/products/", json=product_data)
    assert response1.status_code == 201

    # Second creation with same name should fail
    response2 = client.post("/products/", json=product_data)
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"]

def test_list_products(client):
    # Create two products
    client.post("/products/", json={"name": "Product A", "description": "A", "price": 1.00})
    client.post("/products/", json={"name": "Product B", "description": "B", "price": 2.00})

    response = client.get("/products/")
    assert response.status_code == 200
    products = response.json()
    assert isinstance(products, list)
    assert len(products) >= 2
    names = [p["name"] for p in products]
    assert "Product A" in names
    assert "Product B" in names

def test_get_product_by_id(client):
    # Create a product
    response = client.post("/products/", json={"name": "Unique Product", "description": "Unique", "price": 5.00})
    product_id = response.json()["id"]

    # Retrieve by ID
    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 200
    product = get_response.json()
    assert product["id"] == product_id
    assert product["name"] == "Unique Product"

def test_get_product_not_found(client):
    response = client.get("/products/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found."

def test_update_product(client):
    # Create a product
    response = client.post("/products/", json={"name": "Updatable Product", "description": "Old", "price": 10.00})
    product_id = response.json()["id"]

    # Update product
    update_data = {
        "name": "Updated Product",
        "description": "New Description",
        "price": 15.00
    }
    update_response = client.put(f"/products/{product_id}", json=update_data)
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["id"] == product_id
    assert updated["name"] == update_data["name"]
    assert updated["description"] == update_data["description"]
    assert float(updated["price"]) == update_data["price"]

def test_update_product_duplicate_name(client):
    # Create two products
    client.post("/products/", json={"name": "First Product", "description": "First", "price": 1.00})
    response = client.post("/products/", json={"name": "Second Product", "description": "Second", "price": 2.00})
    second_id = response.json()["id"]

    # Attempt to update second product to have the same name as first
    update_response = client.put(f"/products/{second_id}", json={"name": "First Product"})
    assert update_response.status_code == 409
    assert "already exists" in update_response.json()["detail"]

def test_update_product_not_found(client):
    update_response = client.put("/products/999999", json={"name": "Nonexistent"})
    assert update_response.status_code == 404
    assert update_response.json()["detail"] == "Product not found."

def test_delete_product(client):
    # Create a product
    response = client.post("/products/", json={"name": "Deletable Product", "description": "Delete me", "price": 3.00})
    product_id = response.json()["id"]

    # Delete product
    delete_response = client.delete(f"/products/{product_id}")
    assert delete_response.status_code == 204

    # Ensure product is gone
    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 404

def test_delete_product_not_found(client):
    delete_response = client.delete("/products/999999")
    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Product not found."

def test_create_product_invalid_price(client):
    product_data = {
        "name": "Invalid Price Product",
        "description": "Should fail",
        "price": -5.00
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 422  # Validation error

def test_create_product_missing_name(client):
    product_data = {
        "description": "Missing name",
        "price": 10.00
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 422  # Validation error

def test_create_product_long_description(client):
    product_data = {
        "name": "Long Description Product",
        "description": "x" * 10001,  # Exceeds max length
        "price": 10.00
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 422  # Validation error

# Exported: All test functions for pytest discovery