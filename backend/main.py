import asyncio

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from database import engine, Base
from routers import auth_router, markets_router, users_router
from tokengate import config as tokengate_config
from tokengate import models as tokengate_models  # noqa: F401 (register tables)
from tokengate import router as tokengate_router
from tokengate.recheck import recheck_loop
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Prediction Market", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(markets_router.router)
app.include_router(users_router.router)
app.include_router(tokengate_router.router)


@app.on_event("startup")
async def start_tokengate_recheck():
    if tokengate_config.is_configured():
        app.state.tokengate_recheck = asyncio.create_task(recheck_loop())

# Serve frontend static files if built
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    # Serve static assets under /assets
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    # SPA fallback middleware: serve index.html for non-API, non-asset routes
    class SPAMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            response = await call_next(request)
            # If it's not an API route, not a static asset, and the route wasn't found,
            # serve index.html for SPA routing
            path = request.url.path
            if (
                response.status_code == 404
                and not path.startswith("/api/")
                and not path.startswith("/assets/")
                and not path.startswith("/docs")
                and not path.startswith("/openapi")
                and request.method == "GET"
            ):
                return FileResponse(os.path.join(frontend_dist, "index.html"))
            return response

    app.add_middleware(SPAMiddleware)
