import types
from fastapi.testclient import TestClient
import backend.server as server

# Patch the MongoDB client to avoid real database calls
server.client = types.SimpleNamespace(admin=types.SimpleNamespace(command=lambda *args, **kwargs: {"ok": 1}))

client = TestClient(server.app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
