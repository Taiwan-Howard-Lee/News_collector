# 📚 API Documentation - Instagram Style

## 🌐 Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## 🔐 Authentication
Currently, the API is open for development. In production, implement JWT authentication.

## 📱 Instagram Endpoints

### 📰 Posts

#### GET /instagram/posts
Get Instagram-style posts with engagement data.

**Parameters:**
- `limit` (int, optional): Number of posts to return (default: 20)
- `offset` (int, optional): Number of posts to skip (default: 0)
- `category` (string, optional): Filter by category

**Response:**
```json
{
  "posts": [
    {
      "id": "1",
      "title": "Singapore Launches National AI Strategy 2025",
      "caption": "Singapore launches National AI Strategy 2025 with S$1.5B funding...",
      "imageUrl": "/placeholders/technology.jpg",
      "sourceUrl": "https://example.com/article",
      "sourceName": "Channel NewsAsia",
      "createdAt": "2025-07-14T03:36:56.736488",
      "hashtags": "[\"Singapore\", \"AI\", \"Technology\"]",
      "likesCount": 42,
      "commentsCount": 8,
      "sharesCount": 15,
      "isLiked": false,
      "isBookmarked": false,
      "comments": [],
      "category": "technology",
      "relevanceScore": 0.95
    }
  ],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

#### POST /instagram/posts/{post_id}/like
Like or unlike a post.

**Response:**
```json
{
  "success": true,
  "likes_count": 43,
  "engagement_score": 0.92
}
```

#### POST /instagram/posts/{post_id}/comment
Add a comment to a post (triggers AI response).

**Request Body:**
```json
{
  "comment": "This is great news for Singapore!"
}
```

**Response:**
```json
{
  "success": true,
  "ai_response": "Great to hear you're excited! 🎉 The AI strategy aims to boost our economy...",
  "comments_count": 9,
  "engagement_score": 0.94
}
```

#### POST /instagram/posts/{post_id}/share
Share a post.

**Response:**
```json
{
  "success": true,
  "shares_count": 16,
  "engagement_score": 0.96
}
```

### 📚 Stories

#### GET /instagram/stories
Get Instagram-style stories.

**Response:**
```json
{
  "stories": [
    {
      "id": "daily_briefing",
      "title": "Daily Briefing",
      "imageUrl": "assets/images/daily_briefing.png",
      "content": "Today's top 5 Singapore news highlights",
      "type": "dailyBriefing",
      "createdAt": "2025-07-14T07:27:35.464202",
      "expiresAt": "2025-07-15T07:27:35.464208",
      "isViewed": false,
      "slides": [
        {
          "id": "slide_0",
          "imageUrl": "/placeholders/technology.jpg",
          "title": "Singapore Launches National AI Strategy 2025",
          "text": "Singapore launches National AI Strategy 2025...",
          "duration": 5,
          "actionUrl": "https://example.com/article",
          "actionText": "Read More"
        }
      ],
      "viewsCount": 0
    }
  ]
}
```

### 📊 Analytics

#### GET /instagram/trending
Get trending posts based on engagement.

**Response:**
```json
{
  "trending_posts": [
    {
      "id": "3",
      "title": "Singapore Launches National AI Strategy 2025",
      "engagement_score": 0.95,
      "likesCount": 42,
      "commentsCount": 8,
      "sharesCount": 15
    }
  ]
}
```

#### GET /instagram/categories
Get category statistics.

**Response:**
```json
{
  "categories": [
    {
      "name": "technology",
      "count": 15,
      "icon": "💻"
    },
    {
      "name": "business",
      "count": 12,
      "icon": "💼"
    }
  ]
}
```

### 🖼️ Image Generation

#### POST /instagram/generate-all-images
Generate placeholder images for all posts without images.

**Response:**
```json
{
  "success": true,
  "generated_count": 5,
  "total_posts": 5
}
```

#### POST /instagram/posts/{post_id}/generate-image
Generate image for a specific post.

**Response:**
```json
{
  "success": true,
  "image_url": "/placeholders/technology.jpg",
  "post_id": 1
}
```

## 🔧 Utility Endpoints

#### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "message": "API is running"
}
```

## 📁 Static Files

### Image Serving
- **Cached Images**: `/images/{hash}.jpg`
- **Placeholder Images**: `/placeholders/{category}.jpg`

### Categories
Available placeholder categories:
- `business.jpg` - Business news
- `technology.jpg` - Technology news
- `transport.jpg` - Transport news
- `property.jpg` - Property news
- `politics.jpg` - Politics news
- `finance.jpg` - Finance news
- `education.jpg` - Education news
- `healthcare.jpg` - Healthcare news
- `environment.jpg` - Environment news
- `sports.jpg` - Sports news
- `entertainment.jpg` - Entertainment news

## 🚨 Error Handling

### Common Error Responses

#### 404 Not Found
```json
{
  "detail": "Post not found"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

## 📈 Rate Limiting
- **Development**: No limits
- **Production**: 100 requests per minute per IP

## 🔄 Pagination
All list endpoints support pagination:
- `limit`: Maximum items per page (default: 20, max: 100)
- `offset`: Number of items to skip (default: 0)

## 📱 Response Format
All responses follow consistent format:
- Success responses include relevant data
- Error responses include `detail` field
- Timestamps are in ISO 8601 format
- All engagement counts are integers
- Scores are floats between 0.0 and 1.0

---

**🎉 Ready to build amazing Instagram-style news experiences!**
