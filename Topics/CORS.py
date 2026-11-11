#   on hold 
# CORS is a browser security mechanism that controls whether a frontend from one origin can access a backend from another origin.

# Nothing but when our f and backend are on different port then we neend Cros

# in this we send preflight request (that help that this post can comminicate with the other port );

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,

    # Allowed Frontend URLs
    allow_origins=[
        "http://localhost:3000",  # React
        "http://localhost:5173",  # Vite
    ],

    # Allow Cookies / JWT Headers
    allow_credentials=True,

    # Allow HTTP Methods
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ],

    # Allow Custom Headers
    allow_headers=["*"]
)


@app.get("/")
async def home():
    return {"message": "CORS Enabled Successfully"}