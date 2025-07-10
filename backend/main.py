from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.api import articles as articles_router
from backend.database.connection import init_db, check_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize FastAPI app
app = FastAPI(
    title="Singapore News Intelligence API",
    description="API for accessing processed Singapore news content and interacting with the AI chatbot.",
    version="1.0.0"
)

# --- CORS (Cross-Origin Resource Sharing) --- #
# This allows the frontend (running on a different port) to communicate with the backend.
origins = [
    "http://localhost:3000",  # Next.js default port
    "http://127.0.0.1:3000",
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

# Include the articles router
app.include_router(articles_router.router)

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

@app.on_event("shutdown")
def on_shutdown():
    logging.info("FastAPI application shutting down...")


# To run this application:
# uvicorn backend.main:app --reload
