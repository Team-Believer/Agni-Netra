from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.database import init_db
from backend.app.api.routes import (
    health, dashboard, events, observations, sources, reports, alerts, models
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} API service...")
    init_db()
    logger.info("Agni-Netra database initialized.")
    yield
    logger.info("Shutting down Agni-Netra service.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.TAGLINE,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Next.js frontend (localhost:3000, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(events.router, prefix="/api", tags=["Events"])
app.include_router(observations.router, prefix="/api", tags=["Observations"])
app.include_router(sources.router, prefix="/api", tags=["Sources"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])
app.include_router(alerts.router, prefix="/api", tags=["Alerts"])
app.include_router(models.router, prefix="/api", tags=["Models"])

@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "docs_url": "/docs",
        "api_prefix": settings.API_V1_STR
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
