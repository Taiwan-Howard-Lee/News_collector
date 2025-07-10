import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/news.db")

# PostgreSQL-specific configuration for Railway
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,  # Recycle connections every 5 minutes
        echo=False  # Set to True for SQL debugging
    )
    logger.info("Connected to PostgreSQL database")
else:
    # SQLite for local development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    logger.info("Connected to SQLite database")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize the database by creating all tables.
    """
    from backend.models.article import Base
    from backend.models.user import Base as UserBase
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        UserBase.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def check_db_connection():
    """
    Test database connection.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False 