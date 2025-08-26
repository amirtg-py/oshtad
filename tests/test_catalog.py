import types
from fastapi.testclient import TestClient
import backend.server as server

# Stub database collection
server.products_collection = types.SimpleNamespace(
    aggregate=lambda pipeline: [
        {"_id": "لوازم پزشکی", "image": "img.png"}
    ],
    find=lambda filter, projection: [
        {"id": "1", "name": "محصول ویژه", "featured": True, "price": 1000}
    ]
)

client = TestClient(server.app)

def test_categories_endpoint():
    response = client.get("/api/categories")
    assert response.status_code == 200
    assert response.json() == [{"name": "لوازم پزشکی", "image": "img.png"}]

def test_featured_products_endpoint():
    response = client.get("/api/products/featured")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["featured"] is True
