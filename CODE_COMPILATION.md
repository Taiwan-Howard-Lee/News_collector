# Singapore News Intelligence Dashboard - Complete Code Compilation

## 📋 Project Overview

This is a comprehensive AI-powered Singapore News Intelligence Dashboard with the following architecture:

- **Frontend**: Google Apps Script (HTML Service) with modern UI/UX
- **Backend**: Python FastAPI with PostgreSQL/SQLite database
- **AI Integration**: Google Gemini API for content processing
- **Data Storage**: Google Sheets for presentation layer
- **Scraping**: Asynchronous pipeline for news collection

---

## 🏗️ Project Structure

```
News_collector/
├── 📁 backend/                    # Python backend services
│   ├── 📁 api/                   # FastAPI endpoints
│   ├── 📁 database/              # Database connections & handlers
│   ├── 📁 models/                # SQLAlchemy models
│   ├── 📁 scrapers/              # Web scraping pipeline
│   ├── 📁 utils/                 # Utility functions
│   ├── main.py                   # FastAPI application entry point
│   └── run_scraper.py           # Scraper execution script
├── 📁 gas/                       # Google Apps Script frontend
│   ├── Code.gs                   # Server-side GAS functions
│   ├── Index.html               # Main dashboard UI
│   ├── JavaScript.html          # Client-side JavaScript
│   ├── Stylesheet.html          # CSS styling
│   ├── Onboarding.html          # User onboarding form
│   └── appsscript.json          # GAS configuration
├── 📁 config/                    # Configuration files
├── 📁 data/                      # Data storage
├── 📁 test/                      # Test files
├── PROJECT_PLAN.md              # Detailed project roadmap
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## 🎨 Frontend Code (Google Apps Script)

### 1. Main Dashboard (Index.html)
**Purpose**: Modern, responsive news dashboard with search, filtering, and theme toggle

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <base target="_top">
    <title>Singapore News Intelligence Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="AI-powered Singapore news dashboard with personalized insights">
    <meta name="theme-color" content="#4285F4">
    <?!= include('Stylesheet'); ?>
  </head>
  <body data-theme="light">
    <div class="container">
      <header>
        <h1>Singapore News Intelligence Dashboard</h1>
        <p>Your personalized AI-powered news companion</p>
      </header>
      
      <!-- Controls Section -->
      <section class="controls" role="toolbar" aria-label="News controls">
        <div class="controls-left">
          <div class="search-box">
            <i class="fas fa-search search-icon" aria-hidden="true"></i>
            <input 
              type="text" 
              class="search-input" 
              placeholder="Search articles..." 
              id="search-input"
              aria-label="Search articles"
            >
          </div>
          
          <select class="filter-select" id="source-filter" aria-label="Filter by source">
            <option value="">All Sources</option>
          </select>
          
          <select class="filter-select" id="date-filter" aria-label="Filter by date">
            <option value="">All Dates</option>
            <option value="today">Today</option>
            <option value="yesterday">Yesterday</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
          </select>
          
          <select class="filter-select" id="sort-filter" aria-label="Sort articles">
            <option value="relevance">Sort by Relevance</option>
            <option value="date-desc">Newest First</option>
            <option value="date-asc">Oldest First</option>
            <option value="source">By Source</option>
          </select>
        </div>
        
        <div class="controls-right">
          <button 
            class="theme-toggle" 
            id="theme-toggle" 
            aria-label="Toggle dark mode"
            title="Toggle dark/light theme"
          >
            <i class="fas fa-moon" aria-hidden="true"></i>
          </button>
        </div>
      </section>

      <!-- News Container -->
      <main id="news-container" role="main" aria-label="News articles">
        <!-- Loading state -->
        <div class="loader" id="loader" aria-label="Loading articles">
          <div class="spinner"></div>
        </div>
      </main>

      <!-- Empty State (hidden by default) -->
      <div class="empty-state" id="empty-state" style="display: none;" role="status">
        <div class="empty-state-icon">
          <i class="fas fa-newspaper" aria-hidden="true"></i>
        </div>
        <h3>No articles found</h3>
        <p>Try adjusting your search or filter criteria to find more articles.</p>
      </div>

      <!-- Error State (hidden by default) -->
      <div class="error-state" id="error-state" style="display: none;" role="alert">
        <div class="error-state-icon">
          <i class="fas fa-exclamation-triangle" aria-hidden="true"></i>
        </div>
        <h3>Unable to load articles</h3>
        <p id="error-message">Please try refreshing the page or contact support if the problem persists.</p>
      </div>

      <footer>
        <p>Powered by Google Apps Script & Gemini AI • <span id="last-updated"></span></p>
      </footer>
    </div>

    <?!= include('JavaScript'); ?>
  </body>
</html>
```

### 2. Server-side Logic (Code.gs)
**Purpose**: Google Apps Script backend functions for user management and data retrieval

```javascript
// The ID of your Google Sheet
const SHEET_ID = '1KBIhQMQFfiSxPXS1-tLBF_efVexGcUBvGJx-leX41og';
const USER_PROFILES_SHEET = 'User_Profiles';
const SAVED_INSIGHTS_SHEET = 'Saved_Insights';

/**
 * Main entry point for the web app.
 * Checks if the user has a profile. If so, shows the news dashboard.
 * If not, shows the onboarding survey.
 */
function doGet() {
  setupSheets(); // Ensure required sheets exist
  
  const userEmail = Session.getActiveUser().getEmail();
  const userProfile = getUserProfile(userEmail);

  if (userProfile) {
    // User has a profile, show the main dashboard
    return HtmlService.createTemplateFromFile('Index').evaluate()
        .setTitle('Singapore News Intelligence Dashboard')
        .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
  } else {
    // New user, show the onboarding survey
    return HtmlService.createTemplateFromFile('Onboarding').evaluate()
        .setTitle('Welcome! Tell Us About Yourself')
        .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
  }
}

/**
 * Checks if the required sheets exist and creates them with headers if they don't.
 */
function setupSheets() {
  const spreadsheet = SpreadsheetApp.openById(SHEET_ID);
  
  // Check for User_Profiles sheet
  let userProfilesSheet = spreadsheet.getSheetByName(USER_PROFILES_SHEET);
  if (!userProfilesSheet) {
    userProfilesSheet = spreadsheet.insertSheet(USER_PROFILES_SHEET);
    const headers = ['user_email', 'profile_q1_answer', 'profile_q2_answer', 'profile_q3_answer', 'ai_persona_description', 'engagement_points'];
    userProfilesSheet.appendRow(headers);
    userProfilesSheet.hideSheet();
  }

  // Check for Saved_Insights sheet
  let savedInsightsSheet = spreadsheet.getSheetByName(SAVED_INSIGHTS_SHEET);
  if (!savedInsightsSheet) {
    savedInsightsSheet = spreadsheet.insertSheet(SAVED_INSIGHTS_SHEET);
    const headers = ['insight_id', 'user_email', 'article_id', 'saved_message', 'user_rating (1-5)', 'user_comment', 'timestamp'];
    savedInsightsSheet.appendRow(headers);
    savedInsightsSheet.hideSheet();
  }
}

/**
 * Retrieves a user's profile from the User_Profiles sheet.
 * @param {string} email The user's email address.
 * @returns {Object|null} The user profile object or null if not found.
 */
function getUserProfile(email) {
  const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(USER_PROFILES_SHEET);
  const data = sheet.getDataRange().getValues();
  const headers = data.shift();
  
  for (let i = 0; i < data.length; i++) {
    if (data[i][0] === email) { // email is in the first column
      let profile = {};
      headers.forEach((header, index) => {
        profile[header] = data[i][index];
      });
      return profile;
    }
  }
  return null;
}

/**
 * Saves a new user's profile to the User_Profiles sheet.
 * @param {Object} profileData The user's answers from the survey.
 * @returns {Object} A success or error message.
 */
function saveUserProfile(profileData) {
  try {
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(USER_PROFILES_SHEET);
    const userEmail = Session.getActiveUser().getEmail();
    
    // Check if user already exists to prevent duplicates
    if (getUserProfile(userEmail)) {
      return { status: 'error', message: 'User profile already exists.' };
    }
    
    const newRow = [
      userEmail,
      profileData.q1,
      profileData.q2,
      profileData.q3,
      profileData.q4,
      0 // Initial engagement points
    ];
    
    sheet.appendRow(newRow);
    return { status: 'success' };
  } catch (e) {
    Logger.log(`Error saving user profile: ${e.message}`);
    return { status: 'error', message: e.message };
  }
}

/**
 * Includes the content of another file into the main HTML template.
 */
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

/**
 * Fetches news data from the 'Dashboard' tab of the Google Sheet.
 */
function getNewsData() {
  // This function will eventually be personalized
  try {
    const spreadsheet = SpreadsheetApp.openById(SHEET_ID);
    const sheet = spreadsheet.getSheetByName('Dashboard');
    
    if (!sheet) {
      throw new Error('"Dashboard" sheet not found. Please ensure it exists.');
    }

    const dataValues = sheet.getDataRange().getValues();
    if (dataValues.length < 2) {
      return []; // Return empty array if no data besides headers
    }
    const headers = dataValues.shift(); // Get headers and remove them from the array
    
    const articles = dataValues.map(row => {
      const article = {};
      headers.forEach((header, index) => {
        article[header] = row[index];
      });
      return article;
    });
    
    return articles;

  } catch (e) {
    Logger.log(`Error fetching news data: ${e.message}`);
    return { error: e.message };
  }
}
```

---

## 🔧 Backend Code (Python)

### 1. FastAPI Main Application (backend/main.py)
**Purpose**: Main FastAPI application with CORS, health checks, and database initialization

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.api import resources as resources_router
from backend.database.connection import init_db, check_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize FastAPI app
app = FastAPI(
    title="Information Intelligence API",
    description="API for accessing processed information resources and interacting with the AI platform.",
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

# Include the resources router
app.include_router(resources_router.router)

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
```

### 2. Database Models (backend/models/resource.py)
**Purpose**: SQLAlchemy model for news articles with PostgreSQL optimizations

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from datetime import datetime
import uuid

Base = declarative_base()

class Resource(Base):
    """Database model for information resources (articles, guides, opportunities, etc.) with PostgreSQL optimizations."""

    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True)
    resource_id = Column(String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    source = Column(String(100), nullable=True)
    url = Column(String(500), nullable=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    ai_explanation = Column(Text, nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    relevance_score = Column(Float, default=0.0)
    category = Column(String(100), nullable=True)
    status = Column(String(50), default='active')  # active, outdated, important, archived
    metadata_json = Column(JSONB, nullable=True)  # Flexible metadata storage
    search_vector = Column(TSVECTOR, nullable=True)  # Full-text search vector
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for performance
    __table_args__ = (
        Index('idx_resources_source_date', 'source', 'discovered_at'),
        Index('idx_resources_relevance', 'relevance_score'),
        Index('idx_resources_category', 'category'),
        Index('idx_resources_published', 'published_at'),
        Index('idx_resources_search', 'search_vector', postgresql_using='gin'),
    )

    def __repr__(self):
        return f"<Resource(id={self.id}, title='{self.title[:50]}...', source='{self.source}')>"

    def to_dict(self):
        """Convert resource to dictionary for API responses."""
        return {
            'id': self.id,
            'resource_id': self.resource_id,
            'source': self.source,
            'url': self.url,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'ai_explanation': self.ai_explanation,
            'discovered_at': self.discovered_at.isoformat() if self.discovered_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'relevance_score': self.relevance_score,
            'category': self.category,
            'status': self.status,
            'metadata_json': self.metadata_json,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
```

### 3. Database Connection (backend/database/connection.py)
**Purpose**: Database connection management with PostgreSQL and SQLite support

```python
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'config', '.env'), override=True)
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy import text

from backend.models.resource import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/news.db")
print(f"[DEBUG] Using DATABASE_URL: {DATABASE_URL}")

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
            result = connection.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
```

### 4. Asynchronous Scraping Pipeline (backend/scrapers/async_pipeline.py)
**Purpose**: High-performance concurrent web scraping with thread pool execution

```python
import asyncio
import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from backend.scrapers.sites.channelnewsasia.discoverer import discover_links as cna_discoverer
from backend.scrapers.resource_extractor import extract_resource_content

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def scrape_and_prepare_resource(url: str):
    """
    Asynchronously scrapes a single URL and prepares the resource data dictionary.
    Does not insert into the database.
    """
    logging.info(f"Scraping: {url}")
    loop = asyncio.get_event_loop()

    try:
        # Run synchronous extraction in a thread pool executor
        resource_content = await loop.run_in_executor(
            None,  # Uses the default executor
            extract_resource_content,
            url
        )

        if resource_content and resource_content.get('text'):
            resource_data = {
                'resource_id': f"cna_{uuid.uuid4()}",
                'source': 'Channel NewsAsia',
                'url': url,
                'discovered_at': datetime.utcnow().isoformat(),
                'title': resource_content.get('title'),
                'content': resource_content.get('text'),
                'summary': 'N/A',
                'status': 'active'
            }
            logging.info(f"Successfully scraped: {resource_content.get('title')}")
            return resource_data
        else:
            logging.warning(f"Could not extract content from: {url}")
            return None
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        return None

async def run_async_pipeline(max_workers: int):
    """
    Runs the full scraping pipeline asynchronously using a specified number of workers.
    """
    start_time = time.time()
    logging.info(f"Starting asynchronous pipeline with {max_workers} workers...")

    # Discover links from multiple categories (example, should be modularized)
    source_urls = [
        'https://www.channelnewsasia.com/singapore',
        'https://www.channelnewsasia.com/business',
        'https://www.channelnewsasia.com/sport'
    ]

    all_discovered_links = set()
    logging.info(f"Discovering links from {len(source_urls)} categories...")
    for url in source_urls:
        discovered = cna_discoverer(url)
        all_discovered_links.update(discovered)

    new_links = list(all_discovered_links)
    logging.info(f"Discovered {len(new_links)} new resources to process.")

    if not new_links:
        logging.info("No new resources to process. Pipeline finished.")
        return

    # Set up the thread pool executor
    loop = asyncio.get_event_loop()
    loop.set_default_executor(ThreadPoolExecutor(max_workers=max_workers))

    # Stage 1: Concurrently scrape all new links
    logging.info("--- Stage 1: Scraping all new resources ---")
    tasks = [scrape_and_prepare_resource(link) for link in new_links]
    scraped_resources = await asyncio.gather(*tasks)

    # Filter out failed scrapes
    valid_resources = [resource for resource in scraped_resources if resource is not None]

    resources_processed = len(valid_resources)
    if resources_processed == 0:
        logging.info("No new resources were successfully scraped. Pipeline finished.")
        return

    scraping_duration = time.time() - start_time
    logging.info(f"--- Stage 1 finished in {scraping_duration:.2f} seconds. Scraped {resources_processed} resources. ---")

    # TODO: Insert valid_resources into the PostgreSQL database here
    # (This should be implemented in the next step)

    total_duration = time.time() - start_time
    logging.info(f"--- Pipeline finished. Total duration: {total_duration:.2f} seconds. ---")
```

### 5. Scraper Execution Script (backend/run_scraper.py)
**Purpose**: Command-line interface for running the scraping pipeline

```python
import asyncio
import argparse
import sys
import os

# Add the project root to the Python path to resolve import issues
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.scrapers.async_pipeline import run_async_pipeline

def main():
    """
    Main function to run the asynchronous scraping pipeline.
    Accepts a command-line argument for the number of workers.
    """
    parser = argparse.ArgumentParser(description="Run the asynchronous news scraping pipeline.")
    parser.add_argument(
        '--workers',
        type=int,
        default=10,
        help='The maximum number of concurrent workers for scraping.'
    )
    args = parser.parse_args()

    asyncio.run(run_async_pipeline(max_workers=args.workers))

if __name__ == "__main__":
    main()
```

---

## 🎨 Enhanced Frontend Styling

### Modern CSS Design System (gas/Stylesheet.html)
**Purpose**: Comprehensive design system with dark/light themes, responsive design, and modern UI components

```css
<style>
  :root {
    /* Light theme colors */
    --primary-color: #4285F4;
    --primary-hover: #3367d6;
    --secondary-color: #34a853;
    --accent-color: #ea4335;
    --background-color: #f8f9fa;
    --surface-color: #ffffff;
    --card-background: #ffffff;
    --text-primary: #202124;
    --text-secondary: #5f6368;
    --text-tertiary: #80868b;
    --border-color: #dadce0;
    --border-hover: #bdc1c6;
    --shadow-light: rgba(60, 64, 67, 0.1);
    --shadow-medium: rgba(60, 64, 67, 0.15);
    --shadow-heavy: rgba(60, 64, 67, 0.3);
    --success-color: #137333;
    --warning-color: #f9ab00;
    --error-color: #d93025;
    --info-color: #1a73e8;

    /* Spacing system */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    --spacing-2xl: 48px;

    /* Border radius */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-xl: 16px;

    /* Typography */
    --font-size-xs: 0.75rem;
    --font-size-sm: 0.875rem;
    --font-size-base: 1rem;
    --font-size-lg: 1.125rem;
    --font-size-xl: 1.25rem;
    --font-size-2xl: 1.5rem;
    --font-size-3xl: 2rem;

    /* Transitions */
    --transition-fast: 150ms ease-in-out;
    --transition-normal: 250ms ease-in-out;
    --transition-slow: 350ms ease-in-out;
  }

  /* Dark theme */
  [data-theme="dark"] {
    --background-color: #121212;
    --surface-color: #1e1e1e;
    --card-background: #2d2d2d;
    --text-primary: #e8eaed;
    --text-secondary: #9aa0a6;
    --text-tertiary: #80868b;
    --border-color: #3c4043;
    --border-hover: #5f6368;
    --shadow-light: rgba(0, 0, 0, 0.2);
    --shadow-medium: rgba(0, 0, 0, 0.3);
    --shadow-heavy: rgba(0, 0, 0, 0.5);
  }

  * {
    box-sizing: border-box;
  }

  body {
    font-family: 'Inter', 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    margin: 0;
    background-color: var(--background-color);
    color: var(--text-primary);
    line-height: 1.6;
    font-size: var(--font-size-base);
    transition: background-color var(--transition-normal), color var(--transition-normal);
  }

  .container {
    max-width: 1400px;
    margin: 0 auto;
    padding: var(--spacing-lg);
  }

  /* Header Styles */
  header {
    text-align: center;
    margin-bottom: var(--spacing-2xl);
    position: relative;
  }

  header h1 {
    color: var(--text-primary);
    font-size: var(--font-size-3xl);
    font-weight: 700;
    margin-bottom: var(--spacing-sm);
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  header p {
    color: var(--text-secondary);
    font-size: var(--font-size-lg);
    margin-bottom: var(--spacing-lg);
  }

  /* Controls Section */
  .controls {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-xl);
    padding: var(--spacing-lg);
    background: var(--surface-color);
    border-radius: var(--radius-lg);
    box-shadow: 0 2px 8px var(--shadow-light);
    align-items: center;
    justify-content: space-between;
  }

  .controls-left {
    display: flex;
    gap: var(--spacing-md);
    flex-wrap: wrap;
    align-items: center;
  }

  .controls-right {
    display: flex;
    gap: var(--spacing-sm);
    align-items: center;
  }

  .search-box {
    position: relative;
    min-width: 300px;
  }

  .search-input {
    width: 100%;
    padding: var(--spacing-sm) var(--spacing-md) var(--spacing-sm) 40px;
    border: 2px solid var(--border-color);
    border-radius: var(--radius-md);
    font-size: var(--font-size-base);
    background: var(--surface-color);
    color: var(--text-primary);
    transition: border-color var(--transition-fast);
  }

  .search-input:focus {
    outline: none;
    border-color: var(--primary-color);
  }

  .search-icon {
    position: absolute;
    left: var(--spacing-sm);
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-tertiary);
    font-size: var(--font-size-lg);
  }

  .filter-select {
    padding: var(--spacing-sm) var(--spacing-md);
    border: 2px solid var(--border-color);
    border-radius: var(--radius-md);
    background: var(--surface-color);
    color: var(--text-primary);
    font-size: var(--font-size-sm);
    cursor: pointer;
    transition: border-color var(--transition-fast);
  }

  .filter-select:focus {
    outline: none;
    border-color: var(--primary-color);
  }

  .theme-toggle {
    background: none;
    border: 2px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: var(--spacing-sm);
    cursor: pointer;
    color: var(--text-secondary);
    font-size: var(--font-size-lg);
    transition: all var(--transition-fast);
  }

  .theme-toggle:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
  }

  /* News Container */
  #news-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-2xl);
  }

  /* Card Styles */
  .card {
    background: var(--card-background);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: 0 2px 8px var(--shadow-light);
    transition: all var(--transition-normal);
    display: flex;
    flex-direction: column;
    position: relative;
  }

  .card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px var(--shadow-medium);
    border-color: var(--border-hover);
  }

  .card-header {
    position: relative;
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--border-color);
  }

  .card-relevance {
    position: absolute;
    top: var(--spacing-sm);
    right: var(--spacing-sm);
    background: var(--primary-color);
    color: white;
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-sm);
    font-size: var(--font-size-xs);
    font-weight: 600;
  }

  .card-content {
    padding: var(--spacing-lg);
    flex-grow: 1;
  }

  .card h2 {
    font-size: var(--font-size-xl);
    font-weight: 600;
    margin: 0 0 var(--spacing-sm) 0;
    line-height: 1.4;
  }

  .card h2 a {
    text-decoration: none;
    color: var(--text-primary);
    transition: color var(--transition-fast);
  }

  .card h2 a:hover {
    color: var(--primary-color);
  }

  .card-summary {
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
    line-height: 1.6;
    margin-bottom: var(--spacing-md);
  }

  .card-ai-snippet {
    background: linear-gradient(135deg, #f0f7ff, #e8f4fd);
    border-left: 4px solid var(--primary-color);
    padding: var(--spacing-sm) var(--spacing-md);
    margin: var(--spacing-md) 0;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    font-size: var(--font-size-sm);
    font-weight: 500;
    color: var(--primary-color);
  }

  [data-theme="dark"] .card-ai-snippet {
    background: linear-gradient(135deg, #1a2332, #1e2a3a);
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .container {
      padding: var(--spacing-md);
    }

    header h1 {
      font-size: var(--font-size-2xl);
    }

    .controls {
      flex-direction: column;
      align-items: stretch;
    }

    .controls-left,
    .controls-right {
      justify-content: center;
    }

    .search-box {
      min-width: auto;
    }

    #news-container {
      grid-template-columns: 1fr;
      gap: var(--spacing-md);
    }
  }

  /* Accessibility */
  @media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
  }

  /* Focus styles */
  .card:focus-within {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
  }

  button:focus,
  input:focus,
  select:focus {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
  }
</style>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
```

### Enhanced Client-side JavaScript (gas/JavaScript.html)
**Purpose**: Modern interactive functionality with search, filtering, theming, and responsive design

```javascript
<script>
  // Global variables
  let allArticles = [];
  let filteredArticles = [];
  let currentTheme = 'light';

  /**
   * Initialize the application
   */
  function initializeApp() {
    setupEventListeners();
    loadThemePreference();
    fetchNews();
    updateLastUpdated();
  }

  /**
   * Set up all event listeners
   */
  function setupEventListeners() {
    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    themeToggle.addEventListener('click', toggleTheme);

    // Search functionality
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', debounce(handleSearch, 300));

    // Filter functionality
    const sourceFilter = document.getElementById('source-filter');
    const dateFilter = document.getElementById('date-filter');
    const sortFilter = document.getElementById('sort-filter');

    sourceFilter.addEventListener('change', applyFilters);
    dateFilter.addEventListener('change', applyFilters);
    sortFilter.addEventListener('change', applyFilters);
  }

  /**
   * Toggle between light and dark themes
   */
  function toggleTheme() {
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
  }

  /**
   * Set the theme and update UI
   */
  function setTheme(theme) {
    currentTheme = theme;
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);

    const themeIcon = document.querySelector('#theme-toggle i');
    themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
  }

  /**
   * Apply all filters and sorting
   */
  function applyFilters() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const sourceFilter = document.getElementById('source-filter').value;
    const dateFilter = document.getElementById('date-filter').value;
    const sortFilter = document.getElementById('sort-filter').value;

    // Start with all articles
    filteredArticles = [...allArticles];

    // Apply search filter
    if (searchTerm) {
      filteredArticles = filteredArticles.filter(article =>
        article.title?.toLowerCase().includes(searchTerm) ||
        article.summary?.toLowerCase().includes(searchTerm) ||
        article.content?.toLowerCase().includes(searchTerm)
      );
    }

    // Apply source filter
    if (sourceFilter) {
      filteredArticles = filteredArticles.filter(article => article.source === sourceFilter);
    }

    // Apply date filter
    if (dateFilter) {
      const now = new Date();
      const filterDate = getFilterDate(dateFilter, now);

      filteredArticles = filteredArticles.filter(article => {
        const articleDate = new Date(article.discovered_at);
        return articleDate >= filterDate;
      });
    }

    // Apply sorting
    applySorting(sortFilter);

    // Display filtered results
    displayFilteredNews();
  }

  /**
   * Creates enhanced news card with modern features
   */
  function createCard(article) {
    const discoveredDate = new Date(article.discovered_at).toLocaleDateString();
    const relevanceScore = Math.round((article.relevance_score || 0) * 100);
    const aiSnippet = article.ai_snippet || '';

    return `
      <article class="card" role="article" tabindex="0">
        <div class="card-header">
          ${relevanceScore > 0 ? `<div class="card-relevance" title="Relevance Score">${relevanceScore}%</div>` : ''}
        </div>

        <div class="card-content">
          <h2><a href="${article.url}" target="_blank" rel="noopener noreferrer">${article.title}</a></h2>

          ${aiSnippet ? `<div class="card-ai-snippet" title="AI-generated relevance insight">${aiSnippet}</div>` : ''}

          <div class="card-summary">${article.summary || 'No summary available.'}</div>

          <div class="card-actions">
            <button class="card-action-btn" onclick="saveArticle('${article.article_id || article.resource_id}')" title="Save article">
              <i class="fas fa-bookmark" aria-hidden="true"></i> Save
            </button>
            <button class="card-action-btn" onclick="shareArticle('${article.url}')" title="Share article">
              <i class="fas fa-share" aria-hidden="true"></i> Share
            </button>
            <button class="card-action-btn" onclick="discussArticle('${article.article_id || article.resource_id}')" title="Discuss with AI">
              <i class="fas fa-comments" aria-hidden="true"></i> Discuss
            </button>
          </div>
        </div>

        <div class="card-footer">
          <div class="card-meta">
            <span class="card-source">${article.source}</span>
            <span class="card-date">${discoveredDate}</span>
          </div>
        </div>
      </article>
    `;
  }

  // Article action functions for future implementation
  function saveArticle(articleId) {
    console.log('Saving article:', articleId);
    // TODO: Integrate with Google Apps Script to save to user's saved articles
  }

  function shareArticle(url) {
    if (navigator.share) {
      navigator.share({ title: 'Check out this article', url: url });
    } else {
      navigator.clipboard.writeText(url).then(() => {
        alert('Article URL copied to clipboard!');
      });
    }
  }

  function discussArticle(articleId) {
    console.log('Starting discussion for article:', articleId);
    // TODO: Implement AI chat functionality
  }

  // Initialize app when page loads
  window.addEventListener('load', initializeApp);
</script>
```

---

## 📋 Configuration & Dependencies

### Python Dependencies (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
aiohttp==3.9.1
asyncio==3.4.3
google-api-python-client==2.108.0
google-auth-httplib2==0.1.1
google-auth-oauthlib==1.1.0
```

### Google Apps Script Configuration (gas/appsscript.json)
```json
{
  "timeZone": "Asia/Singapore",
  "dependencies": {
    "enabledAdvancedServices": [
      {
        "userSymbol": "Sheets",
        "version": "v4",
        "serviceId": "sheets"
      }
    ]
  },
  "exceptionLogging": "STACKDRIVER",
  "runtimeVersion": "V8"
}
```

---

## 🚀 Getting Started

### Backend Setup
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp config/.env.example config/.env
# Edit config/.env with your database URL and API keys

# 4. Run the FastAPI server
uvicorn backend.main:app --reload

# 5. Run the scraper
python backend/run_scraper.py --workers 10
```

### Frontend Setup (Google Apps Script)
1. Go to [Google Apps Script](https://script.google.com)
2. Create a new project
3. Copy the code from each gas/ file into corresponding GAS files
4. Update the SHEET_ID in Code.gs with your Google Sheet ID
5. Deploy as a web app

### Database Setup
- **Local Development**: Uses SQLite (automatic)
- **Production**: Configure PostgreSQL URL in environment variables

---

## 🔧 Key Features Implemented

### ✅ Completed Features
- **Modern UI/UX**: Responsive design with dark/light themes
- **User Onboarding**: Personalized profile creation
- **News Dashboard**: Grid layout with search and filtering
- **Asynchronous Scraping**: High-performance concurrent processing
- **Database Integration**: PostgreSQL/SQLite with SQLAlchemy
- **FastAPI Backend**: RESTful API with health checks
- **Google Sheets Integration**: Data storage and presentation layer

### 🚧 In Progress Features
- AI-powered relevance scoring
- Interactive chat interface
- Engagement points system
- Advanced filtering and sorting

### 📋 Next Steps
1. Complete Gemini AI integration for content summarization
2. Implement user engagement tracking
3. Add real-time notifications
4. Deploy to production environment
5. Add comprehensive testing suite

---

This compilation provides a complete overview of the Singapore News Intelligence Dashboard codebase, organized for easy understanding and development. Each component is clearly documented with its purpose and implementation details.
