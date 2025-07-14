# 📱 Singapore News Intelligence Dashboard - Instagram Style

A revolutionary news consumption platform that transforms Singapore news into an engaging Instagram-style experience, featuring AI-powered interactions, beautiful visual content, and social engagement features.

## ✨ Features

### 🎨 Instagram-Style Interface
- **Stories Bar**: Daily briefings and breaking news in story format
- **Post Feed**: News articles as Instagram-style posts with images
- **Smooth Animations**: Professional-grade visual effects and transitions
- **Social Engagement**: Like, comment, share, and bookmark functionality
- **Beautiful Gradients**: Instagram-authentic color schemes and shadows

### 🤖 AI-Powered Intelligence
- **Smart Comments**: AI responds contextually to user comments
- **Auto Hashtags**: Intelligent hashtag generation from content
- **Content Summarization**: AI-powered article summaries
- **Engagement Scoring**: Dynamic relevance and engagement algorithms
- **Trending Algorithm**: Smart content ranking based on interactions

### 🖼️ Visual Content Generation
- **Category Placeholders**: Beautiful gradient images for each news category
- **Image Optimization**: Instagram-square format (1080x1080)
- **Smooth Gradients**: Multi-color diagonal gradients with texture
- **Dynamic Colors**: Category-specific color schemes

### 📊 Advanced Analytics
- **Real-time Engagement**: Live tracking of likes, shares, comments
- **Trending Posts**: Algorithm-based trending content
- **Category Analytics**: Post distribution and engagement by category
- **User Interactions**: Comprehensive engagement metrics

## 🚀 Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: Database ORM with Instagram-style engagement tracking
- **Google Gemini AI**: Advanced language model for AI comments and analysis
- **Pillow**: Image processing and generation
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production deployment

### Frontend
- **Flutter Web**: Cross-platform UI framework with Instagram-style components
- **Riverpod**: State management for real-time updates
- **Material Design 3**: Enhanced with Instagram-style customizations
- **Custom Animations**: Smooth transitions and micro-interactions
- **Responsive Design**: Mobile-first Instagram-like experience

### Database Schema
- **Resources**: Enhanced with engagement fields (likes, comments, shares)
- **Image URLs**: Dynamic image serving and caching
- **Engagement Tracking**: Real-time social interaction metrics
- **AI Integration**: Comment storage and response tracking

## 🎯 Quick Start

### Prerequisites
- Python 3.8+
- Flutter SDK 3.0+
- Git

### 🔧 Backend Setup
```bash
# Clone repository
git clone https://github.com/Taiwan-Howard-Lee/News_collector.git
cd News_collector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp config/.env.example config/.env
# Edit config/.env with your API keys

# Run database migrations (Instagram-style fields)
python backend/database/migrate_instagram.py

# Generate beautiful placeholder images
curl -X POST http://localhost:8000/instagram/generate-all-images

# Start development server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 📱 Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
flutter pub get

# Run development server
flutter run -d web-server --web-port 8080
```

### 🌐 Access Applications
- **Instagram-Style Frontend**: http://localhost:8080
- **API Documentation**: http://localhost:8000/docs
- **Generated Images**: http://localhost:8000/placeholders/[category].jpg

## 📖 API Documentation

### Instagram Endpoints
- `GET /instagram/posts` - Get Instagram-style posts with engagement
- `GET /instagram/stories` - Get daily briefing and breaking news stories
- `POST /instagram/posts/{id}/like` - Like a post
- `POST /instagram/posts/{id}/comment` - Add AI-powered comment
- `POST /instagram/posts/{id}/share` - Share a post
- `GET /instagram/trending` - Get trending posts
- `GET /instagram/categories` - Get category statistics

### Image Generation
- `POST /instagram/generate-all-images` - Generate images for all posts
- `POST /instagram/posts/{id}/generate-image` - Generate image for specific post

## ⚙️ Configuration

### Environment Variables
Create `config/.env` with:
```env
# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///data/news.db

# API Configuration
BASE_URL=http://localhost:8000

# Image Generation
IMAGE_QUALITY=85
IMAGE_SIZE=1080
```

## 🎨 Visual Features

### Stories
- Instagram-style circular avatars with gradient rings
- Smooth animations and transitions
- Daily briefing and breaking news categories
- Auto-expiring 24-hour stories

### Posts
- Beautiful category-based placeholder images
- Smooth like animations with Instagram red
- AI-powered comment system
- Social engagement tracking

### Navigation
- Instagram-style bottom navigation
- Smooth transitions between sections
- Active state indicators with gradients

## 🚀 Deployment

### Backend (Railway)
```bash
# Connect to Railway
railway login
railway link
railway up
```

### Frontend (Netlify)
```bash
# Build for production
flutter build web
# Deploy build/web directory
```

## 🧹 Codebase Structure

```
News_collector/
├── backend/
│   ├── api/           # Instagram-style API endpoints
│   ├── database/      # Database models and migrations
│   ├── models/        # Pydantic models with engagement fields
│   ├── services/      # Image generation and AI services
│   └── utils/         # AI processing utilities
├── frontend/
│   ├── lib/
│   │   ├── models/    # Instagram post and story models
│   │   ├── providers/ # State management
│   │   ├── screens/   # Instagram-style screens
│   │   ├── services/  # API communication
│   │   └── widgets/   # Instagram-style components
│   └── web/           # Web-specific configurations
├── config/            # Environment configuration
├── data/              # Database and generated images
└── docs/              # Documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/instagram-enhancement`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add Instagram-style feature'`
5. Push to the branch: `git push origin feature/instagram-enhancement`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at http://localhost:8000/docs
- Review the Instagram UI README at `INSTAGRAM_UI_README.md`

---

**🎉 Experience news like never before with our Instagram-style interface!**
