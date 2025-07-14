# Google Apps Script Frontend - Singapore News Intelligence Dashboard

This folder contains the Google Apps Script (GAS) frontend code for the Singapore News Intelligence Dashboard. The frontend provides a modern, responsive web interface for users to interact with personalized news content.

## 📁 File Structure

```
gas/
├── Code.gs              # Server-side Google Apps Script functions
├── Index.html           # Main dashboard interface
├── JavaScript.html      # Client-side JavaScript functionality
├── Stylesheet.html      # CSS styling and design system
├── Onboarding.html      # User onboarding and profile creation
├── appsscript.json      # GAS project configuration
└── README.md           # This documentation file
```

## 🚀 Features

### ✅ Implemented Features

#### **Modern UI/UX Design**
- Responsive grid layout for news articles
- Dark/light theme toggle with system preference detection
- Modern design system with consistent spacing, colors, and typography
- Smooth animations and micro-interactions
- Mobile-first responsive design

#### **User Personalization**
- Interactive onboarding flow with progress tracking
- User profile creation and management
- Personalized AI companion configuration
- Engagement points system

#### **News Dashboard**
- Real-time search functionality with debouncing
- Advanced filtering by source, date, and relevance
- Multiple sorting options (relevance, date, source)
- Article cards with AI-generated relevance snippets
- Empty states and error handling

#### **Accessibility & Performance**
- ARIA labels and semantic HTML structure
- Keyboard navigation support
- Reduced motion support for accessibility
- Optimized loading states and skeleton screens

### 🚧 Planned Features
- AI chat interface for article discussions
- Article saving and bookmarking
- Social sharing functionality
- Push notifications for relevant articles
- Advanced analytics and insights

## 🔧 Setup Instructions

### 1. Create Google Apps Script Project
1. Go to [Google Apps Script](https://script.google.com)
2. Click "New Project"
3. Rename the project to "Singapore News Dashboard"

### 2. Add Files
For each file in this folder:
1. In the GAS editor, click the "+" button next to "Files"
2. Choose the appropriate file type:
   - `.gs` files → Script file
   - `.html` files → HTML file
3. Copy the content from each file in this folder
4. Paste into the corresponding GAS file

### 3. Configure Project Settings
1. Copy the content from `appsscript.json`
2. In GAS editor, click on "Project Settings" (gear icon)
3. Check "Show 'appsscript.json' manifest file in editor"
4. Replace the manifest content with the provided configuration

### 4. Set Up Google Sheet
1. Create a new Google Sheet
2. Copy the Sheet ID from the URL
3. In `Code.gs`, update the `SHEET_ID` constant with your Sheet ID
4. The script will automatically create required sheets on first run

### 5. Deploy as Web App
1. Click "Deploy" → "New deployment"
2. Choose type: "Web app"
3. Set execute as: "Me"
4. Set access: "Anyone" (or "Anyone with Google account" for restricted access)
5. Click "Deploy"
6. Copy the web app URL

## 📊 Google Sheets Structure

The application automatically creates the following sheets:

### **User_Profiles** (Hidden)
Stores user onboarding responses and engagement data:
- `user_email`: User's Google account email
- `profile_q1_answer`: Long-term goals
- `profile_q2_answer`: Topics of interest
- `profile_q3_answer`: Content to avoid
- `ai_persona_description`: Preferred AI personality
- `engagement_points`: Gamification points
- `created_at`: Profile creation timestamp
- `last_active`: Last activity timestamp

### **Dashboard** (Visible)
Curated news articles for display:
- `article_id`: Unique article identifier
- `source`: News source name
- `url`: Article URL
- `discovered_at`: Discovery timestamp
- `title`: Article title
- `summary`: Article summary
- `relevance_score`: AI-generated relevance (0-1)
- `ai_snippet`: Personalized relevance explanation

### **Articles** (Hidden)
Raw article data from scraping pipeline:
- `article_id`: Unique identifier
- `source`: Source website
- `url`: Original URL
- `discovered_at`: Discovery timestamp
- `title`: Article title
- `content`: Full article text
- `summary`: Generated summary
- `status`: Processing status

### **Saved_Insights** (Hidden)
User-saved AI insights and ratings:
- `insight_id`: Unique insight identifier
- `user_email`: User who saved the insight
- `article_id`: Related article
- `saved_message`: AI message content
- `user_rating`: User rating (1-5)
- `user_comment`: User's comment
- `timestamp`: Save timestamp

### **Logs** (Hidden)
Application activity logs:
- `timestamp`: Event timestamp
- `level`: Log level (INFO, ERROR, WARN)
- `event`: Event type
- `duration_seconds`: Operation duration
- `details`: Additional details

## 🎨 Design System

### **Color Palette**
- **Primary**: #4285F4 (Google Blue)
- **Secondary**: #34a853 (Google Green)
- **Accent**: #ea4335 (Google Red)
- **Success**: #137333
- **Warning**: #f9ab00
- **Error**: #d93025

### **Typography**
- **Primary Font**: Inter (modern, readable)
- **Fallback**: Roboto, system fonts
- **Sizes**: Responsive scale from 0.75rem to 2rem

### **Spacing System**
- **XS**: 4px
- **SM**: 8px
- **MD**: 16px
- **LG**: 24px
- **XL**: 32px
- **2XL**: 48px

### **Dark Theme Support**
Automatic theme switching with:
- System preference detection
- Manual toggle option
- Persistent user preference storage

## 🔐 Security & Privacy

### **Authentication**
- Uses Google OAuth for user authentication
- Email-based user identification
- Session management through Google Apps Script

### **Data Privacy**
- User profiles stored in private Google Sheets
- No external data sharing
- User controls their own data

### **Permissions Required**
- `https://www.googleapis.com/auth/spreadsheets`: Read/write Google Sheets
- `https://www.googleapis.com/auth/userinfo.email`: User identification
- `https://www.googleapis.com/auth/drive.readonly`: File access (if needed)

## 🧪 Testing

### **Manual Testing Checklist**
- [ ] User onboarding flow works correctly
- [ ] Theme toggle functions properly
- [ ] Search and filtering work as expected
- [ ] Responsive design on mobile devices
- [ ] Error states display appropriately
- [ ] Loading states show during data fetch

### **Browser Compatibility**
- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ⚠️ Internet Explorer (limited support)

## 🚀 Deployment

### **Development**
1. Use "Test deployments" for development
2. Share test URL with stakeholders
3. Iterate based on feedback

### **Production**
1. Create "New deployment" when ready
2. Use versioning for updates
3. Monitor usage through GAS dashboard

## 📈 Analytics & Monitoring

### **Built-in Logging**
- User actions logged to Logs sheet
- Performance metrics tracked
- Error reporting and debugging

### **Engagement Tracking**
- User activity timestamps
- Feature usage statistics
- Engagement points system

## 🔄 Integration with Backend

The frontend integrates with the Python backend through:
- **Google Sheets API**: Data synchronization
- **Shared data models**: Consistent article structure
- **Real-time updates**: Automatic refresh of news content

## 📞 Support & Maintenance

### **Common Issues**
1. **Sheet not found errors**: Ensure SHEET_ID is correct
2. **Permission errors**: Check OAuth scopes
3. **Loading issues**: Verify internet connection and sheet access

### **Updates**
- Monitor Google Apps Script platform updates
- Test new features in development environment
- Maintain backward compatibility

## 🤝 Contributing

When making changes:
1. Test thoroughly in development environment
2. Update documentation as needed
3. Follow existing code style and patterns
4. Consider accessibility and performance impact

---

This frontend provides a modern, user-friendly interface for the Singapore News Intelligence Dashboard, with a focus on personalization, accessibility, and performance.
