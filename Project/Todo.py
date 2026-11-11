# Import :
from fastapi import FastAPI, Request
from Routers import todo_router, user_router
from time import perf_counter
import json

# ------------------------------------ for rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

# ERROR:
# from restapi.response import JSONResponse
# There is no package named "restapi"
from fastapi.responses import JSONResponse

# for the db connect  
from contextlib import asynccontextmanager
from sqlalchemy import text 
from config.db import DEFAULT_SCHEMA_NAME, Base , engine





@asynccontextmanager  # helps you manage resources by running setup code before yield and cleanup code after yield, especially in asynchronous applications like FastAPI.
async def lifespan(app: FastAPI):
    print("Application Starts") # Executed when FastAPI starts
    async with engine.begin() as conn: # Creates a database connection and automatically closes it after the block

        await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{DEFAULT_SCHEMA_NAME}"')) ## Create schema if it doesn't already exist

        await conn.run_sync(Base.metadata.create_all)  # Creates all tables defined in your models if they do not already exist

    yield   # Application becomes available to serve requests

    await engine.dispose() # Application becomes available to serve requests. Properly closes all database connections
    print("Application Stops")


# Creating an Object of FastAPI
app = FastAPI(
    title="TODO APP",
    description="TODO APPLICATION TO ADD TARGET LIST",
    version="1.0.0",
    lifespan=lifespan # # Registers startup and shutdown events
)




# appling the schudler  : ----------------------------------------


# scheduler = AsyncIOScheduler()

# def check_health():
#     print("✅ Healthy Application")

# @app.on_event("startup")
# async def startup():
#     print("STARTUP CALLED")

#     scheduler.add_job(
#         check_health,
#         trigger="interval",
#         seconds=5
#     )

#     scheduler.start()

#     print("SCHEDULER STARTED")

# @app.get("/")
# async def root():
#     return {"msg": "Hello"}



#--------------------------------------------------------------------------------------------=======


# Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# ERROR:
# app.state.request_count was commented,
# but middleware is using it.

# app.state.request_count = 0


# Handling Rate Limit Exception
# app.add_exception_handler(
#     RateLimitExceeded,
#     lambda request, exc: JSONResponse(
#         status_code=429,
#         content={
#             "message": "Too many requests !!!"
#         }
#     )
# )      

#below is the another way to handle the exception 

@app.exception_handler(RateLimitExceeded) # create a route 
async def rate_limit_handler(request:Request,exc:RateLimitExceeded):  # fast way to handle custom error !
    return JSONResponse (
        status_code=429,
        content={
            "details":"Too many Request !!!"
        }
    )

# ERROR:
# @app.add_middleware(SlowAPIMiddleware)
# add_middleware is a method, not a decorator.
app.add_middleware(SlowAPIMiddleware)


# Creating the Linkage b/w app and router
Routes = [todo_router, user_router]

for route in Routes:
    app.include_router(
        router=route,
        prefix="/api"
    )


# Middleware :
# To check requested route, method and response time
@app.middleware("http")
async def request_details(req: Request, call_next):

    print("Path :", req.url.path)
    print("Method :", req.method)

    payload = await req.body()

    sensitive_routes = [
        "/api/user/signin",
        "/api/user/signup"
    ]

    if payload and req.url.path not in sensitive_routes:
        try:
            print("Body :", json.loads(payload))
        except Exception:
            print("Body :", payload.decode())

    start = perf_counter()

    response = await call_next(req)

    end = perf_counter()

    print(f"Time taken: {end - start:.4f} seconds")

    return response