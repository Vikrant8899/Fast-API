"""
Custom middleware using FastAPI's built-in @app.middleware decorator.
Middleware processes requests before they reach route handlers
and responses before they're sent to clients.
"""
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


def setup_middleware(app: FastAPI):
    """
    Register all middleware on the FastAPI app.
    Order matters! Middleware added last runs first on the way in.
    """

    # --- CORS ---
    # Allows browsers from other domains to call your API.
    # Essential when a frontend (React, Vue etc.) is on a different port/domain.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],      # In production, list specific domains e.g. ["https://mysite.com"]
        allow_credentials=True,
        allow_methods=["*"],      # GET, POST, PATCH, DELETE etc.
        allow_headers=["*"],
    )

    # --- Timing middleware ---
    # FastAPI's own decorator style — no Starlette class needed
    @app.middleware("http")
    async def timing_middleware(request: Request, call_next):
        """
        Runs for every request.

        Everything BEFORE call_next  → runs before your route handler
        call_next(request)           → your actual route executes here
        Everything AFTER call_next   → runs before the response goes to the client
        """
        start_time = time.time()

        # Hand off to the route handler
        response = await call_next(request)

        # How long did the whole thing take?
        process_time = time.time() - start_time

        # Stamp it onto the response header so callers can see it
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"

        print(f"⏱️  {request.method} {request.url.path} — {process_time:.4f}s")

        return response

    # --- Request logging middleware ---
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        """
        Logs every incoming request and its response status.
        Useful for debugging — comment out in production if too noisy.
        """
        print(f"🔵 Incoming : {request.method} {request.url.path}")

        response = await call_next(request)

        print(f"🟢 Completed: {request.method} {request.url.path} → {response.status_code}")

        return response
