# Singapore News Intelligence Dashboard

An AI-powered news aggregation and personalization system that curates Singapore news content and presents it through an intelligent, user-friendly interface.

## 🎯 Project Overview

This system combines modern web scraping, AI processing, and personalized user experiences to deliver relevant Singapore news content. It features:

- **Intelligent News Curation**: Automated scraping and processing of Singapore news sources
- **AI-Powered Personalization**: Content relevance scoring based on user profiles
- **Modern Web Interface**: Responsive dashboard with search, filtering, and theming
- **User Engagement**: Personalized onboarding and engagement tracking

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter App    │    │   Python Backend │    │   PostgreSQL/   │
│   (Mobile/Web)   │───▶│   (FastAPI +     │───▶│   SQLite DB     │
│                  │    │   Async Scraping)│    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Local Storage  │    │   Gemini AI     │    │   News Sources  │
│   (Hive/SQLite)  │    │   (Processing)  │    │   (Web Scraping)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
News_collector/
├── 📁 backend/                 # Python backend services
│   ├── 📁 api/                # FastAPI endpoints
│   ├── 📁 database/           # Database connections
│   ├── 📁 models/             # Data models
│   ├── 📁 scrapers/           # Web scraping pipeline
│   ├── 📁 utils/              # Utility functions
│   ├── main.py               # FastAPI application
│   └── run_scraper.py        # Scraper execution
├── 📁 frontend/               # Flutter mobile/web app
│   ├── 📁 lib/               # Dart source code
│   │   ├── 📁 models/        # Data models
│   │   ├── 📁 providers/     # State management
│   │   ├── 📁 screens/       # UI screens
│   │   ├── 📁 services/      # API & storage services
│   │   ├── 📁 widgets/       # Reusable UI components
│   │   └── main.dart         # App entry point
│   ├── 📁 assets/            # Images, icons, animations
│   └── pubspec.yaml          # Flutter dependencies
├── 📁 config/                 # Configuration files
├── 📁 data/                   # Data storage
├── 📁 test/                   # Test files
├── PROJECT_PLAN.md           # Detailed project plan
├── CODE_COMPILATION.md       # Complete code reference
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google Account (for Apps Script and Sheets)
- Google Cloud Project (for API access)

### Backend Setup
```bash
# 1. Clone and navigate to project
cd News_collector

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp config/env.example config/.env
# Edit config/.env with your API keys and database URL

# 5. Run the FastAPI server
uvicorn backend.main:app --reload

# 6. Run the scraper
python backend/run_scraper.py --workers 10
```

### Frontend Setup (Flutter)
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Get Flutter dependencies
flutter pub get

# 3. Run on desired platform
flutter run                    # For connected device
flutter run -d chrome         # For web
flutter run -d macos          # For macOS desktop

# 4. Build for production
flutter build apk             # Android APK
flutter build web             # Web build
flutter build macos           # macOS app
```

## ✨ Features

### ✅ Implemented
- **Modern UI/UX**: Responsive design with dark/light themes
- **User Personalization**: Profile-based content curation
- **Advanced Search**: Real-time filtering and sorting
- **Async Scraping**: High-performance concurrent processing
- **Database Integration**: PostgreSQL/SQLite support
- **Error Handling**: Comprehensive error states and logging

### 🚧 In Development
- AI-powered relevance scoring
- Interactive chat interface
- Real-time notifications
- Advanced analytics

## �️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **PostgreSQL/SQLite**: Database storage
- **AsyncIO**: Concurrent processing
- **BeautifulSoup**: Web scraping

### Frontend
- **Flutter**: Cross-platform mobile/web framework
- **Dart**: Programming language
- **Riverpod**: State management
- **Hive**: Local storage and caching

### AI & Processing
- **Google Gemini API**: Content summarization
- **Custom algorithms**: Relevance scoring
- **Natural language processing**: Content analysis

## � Data Flow

1. **Discovery**: Automated discovery of news articles from Singapore sources
2. **Extraction**: Content extraction and cleaning
3. **Processing**: AI-powered summarization and relevance scoring
4. **Storage**: Structured data storage in Google Sheets
5. **Presentation**: Personalized dashboard display
6. **Interaction**: User engagement and feedback collection

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Google APIs
GOOGLE_SHEETS_CREDENTIALS_PATH=config/credentials.json
GOOGLE_SHEET_ID=your_sheet_id_here

# AI Processing
GEMINI_API_KEY=your_gemini_api_key
```

### Google Sheets Structure
The system automatically creates these sheets:
- **Dashboard**: Curated articles for display
- **Articles**: Raw scraped content
- **User_Profiles**: User personalization data
- **Saved_Insights**: User interactions and feedback
- **Logs**: System activity logs

## 🧪 Testing

```bash
# Run backend tests
python -m pytest test/

# Test scraping pipeline
python backend/run_scraper.py --workers 5

# Test API endpoints
curl http://localhost:8000/api/health
```

## 📈 Performance

- **Concurrent Scraping**: Up to 25 parallel workers
- **Response Time**: <2s average for dashboard load
- **Scalability**: Handles 1000+ articles efficiently
- **Uptime**: 99.9% availability target

## 🔐 Security & Privacy

- **Authentication**: Google OAuth integration
- **Data Privacy**: User data stored in private Google Sheets
- **API Security**: Rate limiting and input validation
- **HTTPS**: Secure communication protocols

## � Documentation

- **[PROJECT_PLAN.md](PROJECT_PLAN.md)**: Detailed project roadmap
- **[CODE_COMPILATION.md](CODE_COMPILATION.md)**: Complete code reference
- **[frontend/README.md](frontend/README.md)**: Flutter app documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## � License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

---

**Built with ❤️ for the Singapore tech community**
