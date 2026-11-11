from fastapi.testclient import TestClient
from Todo import app

client = TestClient(app)


def test_show_routes():
    print(app.openapi()["paths"].keys())
    

#---------------------------------------------------- 
# creating the auto testing for the JWT-protected FastAPI API :   For get all todo

def get_access_token():
    login_response = client.post(
        "/api/user/signin",
        json={
            "email": "aman@example.com",
            "password": "Password@123"
        }
    )

    assert login_response.status_code == 200

    return login_response.json()["Assess_token"]


def test_get_all_todos():
    token = get_access_token()

    print("TOKEN =", token)

    response = client.get(
        "/api/todo/todos",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    print("STATUS =", response.status_code)
    print("BODY =", response.text)

    assert response.status_code == 200


#------------------------------------------------------------ 


def test_without_token():

    response = client.get("/api/todo/todos")

    assert response.status_code == 401


def test_invalid_token():

    response = client.get(
        "/api/todo/todos",
        headers={
            "Authorization": "Bearer abcdefghijklmnop"
        }
    )

    assert response.status_code == 401

#------------------------------------------------------------------------------
# #a#uto testing the post api that create an new #TOdo 
def test_create_todo():
    payload = {
        "name": "string",
        "category": "string",
        "status": False
    }
    response = client.post("/api/todo/create",json=payload)
    
    print(response.status_code)
    print(response.json())
    assert response.status_code == 201