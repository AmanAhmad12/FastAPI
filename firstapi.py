from fastapi import FastAPI

app = FastAPI()

@app.get("/get")

def greet():
    return {
        "Status":"Success",
        "Message":"Hello World !"
    }
