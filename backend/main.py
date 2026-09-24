import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.db.init_db import create_database_if_not_exists

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Execute any startup tasks
    create_database_if_not_exists()
    yield
    # Shutdown tasks

app = FastAPI(
    title="Jewellery ERP System API",
    description="Production-ready backend for Jewellery ERP",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "*"  # Temporary, change in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Jewellery ERP API"}
