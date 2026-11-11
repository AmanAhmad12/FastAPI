# using pytest
from fastapi.testclient import TestClient
from demoapi import app

client = TestClient(app)

def test_home():
    response = client.get("/get") 
    assert response.status_code == 200
    assert response.json() == {
        "Status":"Success",
        "Message":"Hello World !"
        }