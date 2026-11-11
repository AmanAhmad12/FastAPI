from fastapi import FastAPI, HTTPException
import requests


app = FastAPI()


#  Get All TODO
@app.get("/todos")

def Get_Todo_By_external_Api():
    url = "https://jsonplaceholder.typicode.com/todos"
    response = requests.get(url)
    return response.json()


# Get TODO by ID
@app.get("/get/{user_id}")
def Get_Todo_By_external_Api_using_id(user_id:int):
    url = f"https://jsonplaceholder.typicode.com/todos/{user_id}"

    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(
            detail="User_Id Not Found !!!",
            status_code = 404
    )

    return response.json()