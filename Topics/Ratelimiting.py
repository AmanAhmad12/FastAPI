from restapi import RestAPI , Request , Response
from slowapi import Limiter
from slowapi.util import get_remote_address # to get user ip address to check which user uses routes how many time
from slowapi.middleware import SlowAPIMiddleware 
from slowapi.errors import RateLimitExceeded
from restapi.response import JSONResponse
# ----------------------------------------------------------------------------=
# Limiter = keeps count of requests.
#  get_remote_address = identifies the user by IP.
#  SlowAPIMiddleware = checks every request automatically.
#  RateLimitExceeded = exception raised when limit is crossed.
#  Exception Handler = returns a friendly 429 JSON response.
#  app.state.limiter = stores the limiter object inside the application.
#-----------------------------------------------------------------------------=

app = RestAPI()

limiter = limiter(key_func=get_remote_address)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    lambda request , exc : JSONResponse(
        status_code=429,
        content={
            "details":"Too many request !!!"
        }
    )
)

@app.add_middleware(SlowAPIMiddleware)
