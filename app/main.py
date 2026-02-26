from fastapi import FastAPI
from app.models.model import API
from contextlib import asynccontextmanager
from app.db.database import engine, Base

from app.routers.api_router import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # Application runs here

    # Shutdown logic (we'll use later if needed)


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "API Sentinel is running 🚀"}

app.include_router(api_router)