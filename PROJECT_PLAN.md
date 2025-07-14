# Singapore News Intelligence Dashboard - Instagram-Style UI

> **Note:** The FastAPI backend is running and is now production-ready. Selenium fallback is fully implemented for all problematic sites, all sites in websites.md are covered, and the system is schema-compliant.

## 🎯 Project Vision
A revolutionary **Instagram-style news intelligence platform** that transforms how people consume Singapore news through engaging visual content, AI-powered insights, and social-media-like interactions.

### Core Value Proposition
- **Instagram-Style UI**: Stories for breaking news, posts for articles with engaging visuals
- **Visual News Experience**: Screenshots, AI-generated images, and scraped photos
- **AI-Powered Social Features**: Like, comment (AI chat), share, and bookmark
- **Personalized Stories**: Daily briefings and trending topics as story highlights
- **Gamified Engagement**: Social media mechanics applied to news consumption
- **Professional Focus**: Tailored for Singapore professionals with modern UX

## System Architecture

### Technology Stack
- **Backend Processing**: Python 3.11+, FastAPI, SQLAlchemy
- **Database**: PostgreSQL (or SQLite for local dev)
- **AI/ML**: Google Gemini API (or pluggable AI modules)
- **Scraping**: Modular scrapers (e.g., Newspaper3k, Feedparser, Requests, **Crawl4AI with Selenium fallback**)
- **Scheduling**: APScheduler, Celery, or GitHub Actions
- **UI**: Decoupled, can be any frontend (Next.js, React, etc.)

### Architecture Pattern
```
┌──────────────┐    ┌────────────────┐    ┌────────────────┐
│ Python Script│───▶│   AI/ML Layer  │    │ PostgreSQL DB  │
│  (Scraping & │    │ (Summarization,│    │ (Data Storage) │
│  Processing) │    │  Tagging, etc.)│    └────────────────┘
└───────┬──────┘                                  │
        │                                         ▼
        └────────────────────────────────▶┌────────────────┐
                                          │ Any Frontend   │
                                          │ (UI, API, etc.)│
                                          └────────────────┘
```

## Core Components

### 1. Data Ingestion Pipeline (Python)
**Purpose**: Automated collection and processing of diverse information (news, guides, opportunities, content, etc.)

**Implementation Strategy**:
- Modular scrapers for each source/type
- Unified, domain-agnostic data model ("Resource")
- Pluggable pipeline for normalization, enrichment, and storage
- **Primary extraction via Crawl4AI; fallback to Selenium-based crawlers for sites with paywalls, anti-bot, or poor extraction.**
- **Selenium-based site-specific crawlers are now implemented for all problematic domains (WSJ, Bloomberg, HBR, CNN, CNBC, Investopedia, Shopify, FT, Invesco).**
- **All sites in websites.md are covered and tested.**
- **All extracted resources are schema-compliant.**

---

### Fallback Logic: Crawl4AI + Selenium

- The system first attempts to extract content using Crawl4AI for all sites.
- If Crawl4AI fails (due to paywall, anti-bot, or poor extraction/quality), the orchestrator automatically retries extraction using a Selenium-based crawler for that domain.
- Selenium-based crawlers use a real browser (headless Chrome/Firefox) to render the page and extract the main article content, bypassing most paywalls and anti-bot measures.
- This fallback logic is fully automated and transparent to the user/API.

**Sites requiring Selenium fallback:**
- Invesco
- WSJ (Wall Street Journal)
- CNN
- CNBC
- Investopedia
- Shopify
- HBR (Harvard Business Review)
- Bloomberg
- FT (Financial Times)

---

### Implementation Steps for Selenium Fallback

- [x] Add Selenium and ChromeDriver/GeckoDriver to requirements and setup
- [x] Implement `SeleniumBaseCrawler` with robust content extraction utilities
- [x] Create site-specific Selenium crawlers for each problematic domain
- [x] Update orchestrator to try Crawl4AI first, then Selenium if needed
- [x] Add tests for fallback logic and extraction quality
- [x] Document fallback mechanism and update developer docs
- [x] All sites in websites.md are covered and tested
- [x] All extracted resources are schema-compliant

---

## Lazy Rehydration and Data Freshness
To optimize storage and ensure data relevance:
- Outdated resources (by time or policy) have heavy fields (content, summary, embeddings, explanations) deleted, but metadata and URL are retained.
- If a user requests an outdated resource, the system re-crawls and reprocesses it, restoring heavy fields and marking it as important.
- Important resources are exempt from future time-based deletion, creating a user-driven, self-healing cache of relevant content.

---

## Current Status

### ✅ Completed Tasks
- [x] Modular backend architecture (FastAPI, SQLAlchemy)
- [x] Database models (Resource, User, extensible for other information types)
- [x] AI Processor utility with Gemini API integration
- [x] Automated scheduler with APScheduler
- [x] FastAPI endpoints for resources and statistics
- [x] Environment configuration template
- [x] Selenium fallback for all problematic sites
- [x] All sites in websites.md are covered and tested
- [x] All extracted resources are schema-compliant
- [x] Comprehensive test coverage
- [x] Git repository setup with .gitignore

### 🚀 Ready for Production
- All core features are implemented and tested.
- The system is production-ready for all listed sites.

# Final Summary

All requirements for the Information Intelligence Platform Backend have been met:
- Selenium fallback is fully implemented for all problematic sites
- All sites previously listed in websites.md are covered and tested
- All extracted resources are schema-compliant and production-ready
- The system is robust, modular, and ready for further expansion

## 📱 Instagram-Style UI Implementation Plan

### Phase 1: Core Instagram UI Components (Week 1)
- [ ] Create Instagram-style post components with image placeholders
- [ ] Implement stories carousel at the top
- [ ] Add bottom navigation (Home, Search, Reels, Profile)
- [ ] Design post feed with engagement buttons (like, comment, share, save)
- [ ] Implement basic story viewer with progress indicators

### Phase 2: Visual Content Generation (Week 2)
- [ ] Web screenshot capture system using Playwright/Puppeteer
- [ ] AI image generation integration (DALL-E/Midjourney API)
- [ ] Image scraping from article pages
- [ ] Image optimization and caching system
- [ ] Fallback placeholder images for articles

### Phase 3: Social Features & Engagement (Week 3)
- [ ] Like/bookmark functionality with local storage
- [ ] AI chat system as "comments" feature
- [ ] Share functionality (native sharing)
- [ ] User engagement tracking and analytics
- [ ] Push notifications for breaking news stories

### Phase 4: Advanced Instagram Features (Week 4)
- [ ] Story highlights system for daily briefings
- [ ] Advanced personalization algorithms
- [ ] Story creation for breaking news (24h expiry)
- [ ] Analytics dashboard for engagement metrics
- [ ] User profile with reading history and preferences

### 🎨 UI/UX Design System
- **Stories**: Breaking news, daily briefings, trending topics, category highlights
- **Posts**: Article cards with hero images, captions, hashtags, engagement metrics
- **Navigation**: Instagram-style bottom tabs and side menu
- **Colors**: Dark theme with Singapore-inspired accent colors
- **Typography**: Modern, readable fonts optimized for mobile

### 📊 Data Model Extensions
```python
# Enhanced Article Model for Instagram-style posts
class InstagramPost:
    - article_id: str
    - image_url: str (screenshot/generated/scraped)
    - caption: str (AI-enhanced title + summary)
    - hashtags: List[str] (AI-generated)
    - likes_count: int
    - comments: List[AIComment] (AI chat history)
    - story_highlight: bool (for stories)
    - engagement_metrics: dict
    - created_at: datetime
    - expires_at: datetime (for stories)
```

**The project is now evolving into a revolutionary Instagram-style news platform that will transform how people consume Singapore news.**