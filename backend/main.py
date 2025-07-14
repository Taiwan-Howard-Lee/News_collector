from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os

from backend.api import resources, instagram
from backend.database.connection import init_db, check_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize FastAPI app
app = FastAPI(
    title="Singapore News Intelligence API",
    description="Instagram-style news intelligence platform API for Singapore news aggregation and AI-powered insights.",
    version="2.0.0"
)

# --- CORS (Cross-Origin Resource Sharing) --- #
# This allows the frontend (running on a different port) to communicate with the backend.
origins = [
    "http://localhost:3000",  # Next.js default port
    "http://127.0.0.1:3000",
    "http://localhost:8080",  # Flutter web default
    "http://localhost:8081",  # Flutter web alternative
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints --- #

@app.get("/api/health", tags=["System"], summary="Check API Health")
def health_check():
    """
    Endpoint to verify that the API is running and healthy.
    """
    logging.info("Health check endpoint was called.")
    return {"status": "ok", "message": "API is running"}

# Include API routers
app.include_router(resources.router)
app.include_router(instagram.router)

# Mount static files for images
os.makedirs("data/images", exist_ok=True)
os.makedirs("data/placeholders", exist_ok=True)
app.mount("/images", StaticFiles(directory="data/images"), name="images")
app.mount("/placeholders", StaticFiles(directory="data/placeholders"), name="placeholders")

# --- Application Startup --- #
@app.on_event("startup")
async def on_startup():
    logging.info("FastAPI application starting up...")
    
    # Initialize database
    try:
        init_db()
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
    
    # Check database connection
    if check_db_connection():
        logging.info("Database connection verified")
    else:
        logging.error("Database connection failed")


# To run this application:
# uvicorn backend.main:app --reload
