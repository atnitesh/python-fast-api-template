import time
from uuid import uuid4
from fastapi import FastAPI, Request, Response
import structlog
import uvicorn
from .utils.logger import logger

from .routers import demo

app = FastAPI(dependencies=[])

@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    structlog.contextvars.clear_contextvars()
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    structlog.contextvars.bind_contextvars(request_id=request_id)
    start_time = time.perf_counter_ns()
    response = await call_next(request)
    end_time = time.perf_counter_ns()
    duration = (end_time - start_time) / 1000000
    logger.info("request recieved", request={
        "method": request.method,
        "path": request.url.path,
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "ip": request.client.host,
    },
        response={
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "ms": duration,
    })
    return response


app.include_router(demo.router, prefix="/demo", tags=["demo"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
