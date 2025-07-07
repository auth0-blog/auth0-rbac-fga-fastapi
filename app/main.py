from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.routes import organization_routes, project_manager_routes, role_routes, permission_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting {settings.app_title} v{settings.app_version}")
    print(f"OpenFGA API URL: {settings.openfga_api_url}")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    description="""
    A FastAPI application demonstrating OpenFGA integration for organization management.
    
    This API provides endpoints for:
    - Managing organizations
    - Assigning project managers
    - Role-based access control
    - Permission checking
    
    All authorization is handled through OpenFGA.
    """
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    organization_routes.router, 
    prefix="/organizations", 
    tags=["organizations"]
)
app.include_router(
    project_manager_routes.router, 
    prefix="/project-managers", 
    tags=["project_managers"]
)
app.include_router(
    role_routes.router, 
    prefix="/roles", 
    tags=["roles"]
)
app.include_router(
    permission_routes.router, 
    prefix="/permissions", 
    tags=["permissions"]
)

@app.get("/")
async def read_root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.app_title}!",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}