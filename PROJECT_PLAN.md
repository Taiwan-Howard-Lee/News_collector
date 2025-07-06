# Singapore News Intelligence Dashboard

## Project Vision
An AI-powered dashboard that aggregates, processes, and visualizes Singapore news content. The system intelligently curates local news and presents it in a clear, accessible interface built with Google Sheets and Google Apps Script.

## System Architecture

### Technology Stack
- **UI & Data Storage**: Google Sheets & Google Apps Script (HTML Service)
- **Backend Processing**: Python 3.11 Script
- **AI/ML**: Google Gemini API
- **Scraping**: Newspaper3k, Feedparser, Requests
- **Scheduling**: Local Cron, Python APScheduler, or GitHub Actions

### Architecture Pattern
```
┌──────────────┐    ┌────────────────┐    ┌────────────────┐
│ Python Script│───▶│   Gemini API   │    │ Google Sheets  │
│  (Scraping &  │    │ (Summarization)│    │      API       │
│  Processing) │    └────────────────┘    └────────────────┘
└───────┬──────┘                                  │
        │                                         ▼
        └────────────────────────────────▶┌────────────────┐
                                          │ Google Sheets  │
                                          │ (Data Storage) │
                                          └───────┬────────┘
                                                  │
                                                  ▼
                                          ┌────────────────┐
                                          │ Google Apps    │
                                          │  Script Web App│
                                          │      (UI)      │
                                          └────────────────┘
```

## Core Components

### 1. Data Ingestion Pipeline (Python)
**Purpose**: Automated collection and processing of Singapore news content.

**Implementation Strategy**:
- The core scraping and processing logic remains the same, implemented as a Python script.
- The final step is to load the structured data (titles, summaries, URLs, etc.) into a designated Google Sheet via the Google Sheets API.

### 2. Content Intelligence Layer (Python)
**Purpose**: To enrich the raw content with AI-generated summaries and relevance scores.

**AI Processing Pipeline**:
- This layer remains part of the Python script.
- It uses the Gemini API to generate concise summaries before writing the data to Google Sheets.

### 3. User Interface (Google Apps Script)
**Purpose**: To provide a clean, interactive dashboard for viewing the curated news.

**Architecture**:
- A single Google Apps Script project will be attached to the central Google Sheet.
- The web app, built using GAS `HTML Service`, will read data **exclusively from the `Dashboard` tab**. This ensures the UI is decoupled from the raw data ingestion process.

**UI Features**:
- **News Dashboard**: Display articles in a tabular or card-based layout.
- **Filtering & Sorting**: Allow users to filter articles by source, date, or relevance score.
- **Direct Links**: Provide direct links to the original articles.

## Data Storage (Google Sheets)

A single Google Sheet will serve as the central database, organized into five key tabs to ensure a clear separation of data, user profiles, and logs.

1.  **`Articles` (Raw Data Tab)**:
    - **Purpose**: This sheet acts as the primary data dump for the Python scraper. All articles from all sources are appended here.
    - **Columns**: `article_id`, `source`, `url`, `discovered_at`, `title`, `content`, `summary`, `status`.

2.  **`Dashboard` (Presentation Tab)**:
    - **Purpose**: This sheet uses formulas (e.g., `=QUERY` or `=FILTER`) to pull curated data from the `Articles` tab. It serves as the clean data source for the Google Apps Script UI.
    - **Columns**: Can be a subset or reordered version of the `Articles` columns, tailored for display.

3.  **`Logs` (Monitoring Tab)**:
    - **Purpose**: Captures logs from the Python script to monitor scraping sessions.
    - **Columns**: `timestamp`, `level`, `event`, `duration_seconds`, `details`.

4.  **`User_Profiles` (Hidden Tab)**:
    - **Purpose**: Stores user-specific data, including their preferences and AI persona settings.
    - **Columns**: `user_email`, `profile_q1_answer`, `profile_q2_answer`, `profile_q3_answer`, `ai_persona_description`, `engagement_points`.

5.  **`Saved_Insights` (Hidden Tab)**:
    - **Purpose**: Stores specific insights that users save from their discussions with the AI.
    - **Columns**: `insight_id`, `user_email`, `article_id`, `saved_message`, `user_rating (1-5)`, `user_comment`, `timestamp`.

## Development Phases

### Phase 1: Foundation (Weeks 1-2)
**Data Pipeline Development**
- Refine scraping and processing Python script.
- **[DONE]** Integrate Google Sheets API to write data to the `Articles` and `Logs` sheets.
- **[DONE]** Implement Asynchronous Pipeline for High-Performance Scraping.
  - Developed a new asynchronous pipeline (`backend/scrapers/async_pipeline.py`) using `asyncio` and a `ThreadPoolExecutor` to process articles concurrently.
  - Scaled and tested the pipeline with up to 25 workers, significantly improving data ingestion speed.
  - Refactored the pipeline into a two-stage process (concurrent scraping followed by batch insertion) to resolve Google Sheets API connection limits and maximize throughput.
- Basic Gemini API integration for summaries.

### Phase 2: Intelligence Layer (Week 3)
**AI Integration & Processing**
- Implement relevance scoring within the Python script.
- Optimize batch processing for API calls.

### Phase 3: The AI News Companion (Weeks 4-6)
**Building a Personalized, Interactive News Experience**

This phase moves beyond a simple dashboard to create a sophisticated, AI-powered news companion.

**Phase 3.1: Foundation - Personalization Engine**
- **User Identity**: Identify users via their Google Account email.
- **User Onboarding**: Create a one-time, 4-question survey to establish a rich user profile. The final question will define the user's desired AI chat persona.
- **Data Storage**: Implement a new hidden sheet, `User_Profiles`, to store user emails, profile answers, and engagement points.

**Phase 3.2: Core AI - Relevance & Insight**
- **AI Ranking**: The backend pipeline will use the user's profile to generate a relevance score for each article, sorting the main feed.
- **Two-Layer Explanation**:
    - **On-Card Snippet**: The AI will generate a short, bolded sentence on each news card summarizing its relevance.
    - **On-Demand Explanation**: A "Why is this relevant?" button will trigger a more detailed, on-the-fly analysis from the AI.

**Phase 3.3: Interactive AI Discussion**
- **AI Chat Persona**: The chat AI will adopt the personality defined by the user in their profile.
- **Chat Interface**: Develop the UI for the one-on-one discussion chatroom.
- **Save & Rate Insights**: Allow users to save key messages from the AI, rate them (1-5 stars), and add comments. Store these in a new `Saved_Insights` sheet.

**Phase 3.4: Engagement Loop - Gamification**
- **Personal Points System**: Implement a simple, personal point system to encourage engagement.
- **Rewarded Actions**:
    - Award points for reading an article.
    - Award more significant points for engaging in a discussion where the AI tests and validates the user's understanding of the article's content.
- Write GAS functions to read data from the Sheet and serve it to the UI.

### Phase 4: Deployment & Automation (Week 6)
**Automation & Monitoring**
- Set up a scheduler (e.g., cron job, GitHub Action) to run the Python script periodically.
- Deploy the Google Apps Script as a web app.
- Finalize documentation.

## Risk Management

### Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Source website changes | High | RSS-first strategy, robust selectors |
| API rate limits | Medium | Intelligent batching, exponential backoff |
| Google Sheets performance | Medium | Limit sheet size, implement archiving script |

## Development Environment

### Prerequisites
```bash
# Python environment
python 3.11+
pip install -r backend/requirements.txt

# Google Cloud Authentication
# Set up a service account and download credentials.json
# See Google Cloud documentation for details.

# Environment variables
GEMINI_API_KEY=your_key_here
GOOGLE_SHEET_ID=your_sheet_id_here
```

### Local Development
```bash
# To run the backend scraper script
cd backend
python pipeline.py
```

### Deployment
1.  **Backend**: Schedule the `pipeline.py` script to run on a server, a local machine with cron, or using a service like GitHub Actions.
2.  **Frontend**: In the Google Apps Script editor, go to `Deploy` > `New deployment`, select `Web app`, and configure access permissions.

This architecture prioritizes simplicity, rapid development, and low operational overhead by leveraging the Google Workspace ecosystem.

## Current Status

### ✅ Completed Tasks
- [x] Project planning and architecture design (Initial & Revised)
- [x] Google Sheets API Integration & Authentication Setup
- [x] Refactored `g_sheets.py` into a reusable module
- [x] Test infrastructure setup in `/test` folder
- [x] Successful testing with CapitaLand and Business Times URLs
- [x] **NEW**: Database models (Article, User) with SQLAlchemy
- [x] **NEW**: AI Processor utility with Gemini API integration
- [x] **NEW**: Automated scheduler with APScheduler
- [x] **NEW**: FastAPI endpoints for articles and statistics
- [x] **NEW**: Comprehensive project structure with proper organization
- [x] **NEW**: Environment configuration template
- [x] **NEW**: Git repository setup with .gitignore

### 🚧 In Progress
- [ ] Database connection and session management
- [ ] RSS feed integration and parsing
- [ ] Integration of AI processor with scraping pipeline
- [ ] Frontend development (Next.js)

### 📋 Next Steps
1. **Database Integration**: Connect SQLAlchemy models to the scraping pipeline
2. **RSS Feed Parser**: Implement RSS feed parsing for primary news sources
3. **AI Integration**: Connect the AI processor to the article processing pipeline
4. **Frontend Development**: Build the Next.js frontend with React components
5. **Deployment**: Set up Railway deployment for the full stack application
6. **Testing**: Comprehensive testing of all components
7. **Documentation**: Complete API documentation and user guides