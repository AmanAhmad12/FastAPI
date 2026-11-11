import json
from time import perf_counter
from fastapi import FastAPI, Request

app = FastAPI()

app.state.request_count=0 # state variable means we can use this variable inside the whole appilcation 
    #   state is like a dict and request_count is one key inside the state

#--------------------------------------------------------------

# Middleware is a method that applay on each and every routes 
# it is used for validating , auth , some business logic 

#--------------------------------------------------------------

# ┌──────────────────────────────────────────────────────────┐
# │  MIDDLEWARE (Phase 1: Pre-Processing)                   │
# │                                                          │
# │  1. Capture path (req.url.path) & method (req.method)    │
# │  2. Read body bytes (await req.body()) & print JSON      │
# │  3. Re-pack body into a new Request stream (req)         │
# │  4. Start timer (start = perf_counter())                 │
# └──────────────────────────┬───────────────────────────────┘

@app.middleware("http")
async def request_details(req: Request, call_next): 
#   ------------------------------------------------------------------=
#   call_next     A function that receives req as an argument 
#   and passes it along to the target route handler (or next middleware).

    # Print request path and HTTP method
#   ------------------------------------------------------------------=
    print(req.url.path)
    print(req.method)
    # print(req["path"]) # second method 
    # print(req["method"]) # second way 
    # Read request body safely
    payload = await req.body()

    if payload:
        print(json.loads(payload)) # json.loads() converts the raw JSON byte string into a Python dictionary/list 

    # Time the request execution
    start = perf_counter()
    app.state.request_count += 1 # incrementing the count when we use routes 
    print(app.state.request_count)
    response = await call_next(req)
    
#-----------------------------------------------------------
#   I am done inspecting the incoming request. Now, hand it over to the route
#    handler to do its work, and give me back the result when it's done
#-----------------------------------------------------------

    end = perf_counter()

    print(f"Time taken: {end - start:.4f} seconds")

    return response