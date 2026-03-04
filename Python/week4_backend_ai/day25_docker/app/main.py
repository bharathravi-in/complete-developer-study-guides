#!/usr/bin/env python3
"""Sample FastAPI Application for Docker Demo"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import os

app = FastAPI(
    title="Docker Demo API",
    description="Sample API for Docker deployment",
    version="1.0.0"
)


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    environment: str


class Item(BaseModel):
    name: str
    price: float


# In-memory storage
items = {}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Docker Demo API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Docker."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        environment=os.getenv("ENVIRONMENT", "development")
    )


@app.get("/items")
async def get_items():
    """Get all items."""
    return {"items": items}


@app.get("/items/{item_id}")
async def get_item(item_id: str):
    """Get single item."""
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]


@app.post("/items/{item_id}")
async def create_item(item_id: str, item: Item):
    """Create new item."""
    if item_id in items:
        raise HTTPException(status_code=400, detail="Item already exists")
    items[item_id] = item.model_dump()
    return {"message": "Item created", "item": items[item_id]}


@app.get("/env")
async def get_env():
    """Show environment configuration (non-sensitive)."""
    return {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug": os.getenv("DEBUG", "false"),
        "database_configured": bool(os.getenv("DATABASE_URL")),
        "redis_configured": bool(os.getenv("REDIS_URL")),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
