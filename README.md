# Singapore News Intelligence Chatbot

An AI-powered conversational interface that aggregates, processes, and personalizes Singapore news content. The system intelligently curates local news based on user-defined relevance criteria and delivers insights through natural conversation.

## 🏗️ Project Structure

```
News_collector/
├── backend/                 # Python FastAPI backend
│   ├── api/                # REST API endpoints
│   ├── core/               # Core business logic
│   ├── scrapers/           # News scraping modules
│   ├── models/             # Database models
│   └── utils/              # Utility functions
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Next.js pages
│   │   ├── hooks/          # Custom React hooks
│   │   └── utils/          # Frontend utilities
│   └── public/             # Static assets
├── config/                 # Configuration files
├── data/                   # Data storage
│   ├── raw/               # Raw scraped data
│   └── processed/         # Processed data
├── logs/                   # Application logs
├── test/                   # Test files
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```

## 🚀 Technology Stack

- **Frontend**: Next.js 14, React 18, Tailwind CSS
- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Database**: SQLite with WAL mode
- **AI/ML**: Google Gemini 2.0 Lite API
- **Scraping**: Trafilatura, Feedparser, Requests
- **Deployment**: Railway (containerized)
- **Process Management**: APScheduler for background tasks

## 📋 Features

### Core Functionality
- ✅ **Automated News Scraping**: RSS feeds + web scraping from Singapore news sources
- ✅ **AI-Powered Summarization**: Gemini 2.0 Lite for content processing
- ✅ **Relevance Scoring**: Personalized content ranking based on user preferences
- ✅ **Conversational Interface**: Natural language chat with article recommendations
- ✅ **Real-time Updates**: Live article suggestions during conversations

### News Sources
- **Primary (RSS)**: Channel NewsAsia, TODAY, Business Times, Yahoo Singapore
- **Secondary (Web Scraping)**: Mothership, Rice Media, AsiaOne, The New Paper

## 🛠️ Development Setup

### Prerequisites
```bash
# Python 3.11+
python --version

# Git
git --version
```

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/Taiwan-Howard-Lee/News_collector.git
cd News_collector
```

2. **Run the setup script**
```bash
python scripts/setup.py
```

3. **Configure environment variables**
```bash
# Copy environment template
cp config/env.example config/.env

# Edit with your API keys
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_SHEET_ID=your_google_sheet_id_here
```

4. **Add Google Cloud credentials**
```bash
# Place your service account JSON file at:
config/credentials.json
```

### Manual Setup (Alternative)

1. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
# Copy environment template
cp config/env.example config/.env

# Edit with your API keys
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_SHEET_ID=your_google_sheet_id_here
```

### Running the Application

**Development Mode:**
```bash
# Backend API Server (Terminal 1)
cd backend
uvicorn main:app --reload --port 8000

# Scraper (Terminal 2)
cd backend
python run_scraper.py

# Google Apps Script (Deploy separately)
# Deploy the gas/ folder as a Google Apps Script web app
```

**Access the application:**
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Google Apps Script Dashboard: (Deploy from gas/ folder)

## 🧪 Testing

```bash
# Run all tests
cd test
python run_tests.py

# Run specific tests
python test_trafilatura_scraper.py
python detailed_test_results.py
```

## 📊 Current Status

### ✅ Completed
- [x] Project architecture and planning
- [x] Google Sheets API integration
- [x] Database models (SQLAlchemy)
- [x] AI processor with Gemini API
- [x] Automated scheduler (APScheduler)
- [x] FastAPI endpoints
- [x] Google Apps Script UI components
- [x] Test infrastructure setup
- [x] Comprehensive project structure

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

## 🔧 Configuration

Key configuration files:
- `config/.env` - Environment variables
- `config/sources.json` - News source definitions
- `config/scraping.json` - Scraping parameters
- `backend/requirements.txt` - Python dependencies
- `frontend/package.json` - Node.js dependencies

## 📈 Monitoring

The system includes comprehensive monitoring:
- **Database Stats**: Article counts, source performance
- **Scraping Logs**: Success/failure rates, execution times
- **API Usage**: Gemini API costs and rate limits
- **System Health**: Uptime, response times

## 🚀 Deployment

**Railway Deployment:**
```bash
railway login
railway init
railway up
```

**Docker Deployment:**
```bash
docker-compose up -d
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

For questions or issues, please:
1. Check the documentation in `/docs`
2. Review existing issues
3. Create a new issue with detailed information

---

**Built with ❤️ for Singapore news intelligence**
