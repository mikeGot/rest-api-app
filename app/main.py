from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import activities, buildings, organizations

app = FastAPI(
    title="REST API - Organizations Catalog",
    description="""
    REST API application for managing Organizations, Buildings, and Activities catalog.

    ## Features
    - **Organizations**: Manage organization entries with contact information
    - **Buildings**: Manage buildings with geographic coordinates
    - **Activities**: Hierarchical activity classification (max 3 levels)

    ## Authentication
    All endpoints require API Key authentication via `X-API-Key` header.

    ## Search Capabilities
    - Search organizations by building
    - Search by activity (includes child activities in tree)
    - Geo-spatial search by radius or rectangle
    - Search by name
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(organizations.router, prefix="/api/v1")
app.include_router(buildings.router, prefix="/api/v1")
app.include_router(activities.router, prefix="/api/v1")


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "REST API - Organizations Catalog",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0",
    }


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}
