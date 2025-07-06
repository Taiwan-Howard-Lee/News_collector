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
 * Fetches personalized news data from the 'Dashboard' tab with AI relevance scoring.
 * @returns {Array} Array of articles with personalized relevance data.
 */
function getNewsData() {
  try {
    const userEmail = Session.getActiveUser().getEmail();
    const userProfile = getUserProfile(userEmail);
    
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
      
      // Add personalized relevance data if user profile exists
      if (userProfile) {
        article.relevance_score = generateRelevanceScore(article, userProfile);
        article.ai_snippet = generateAISnippet(article, userProfile);
        article.user_points = userProfile.engagement_points;
      }
      
      return article;
    });
    
    // Sort by relevance score if available
    if (userProfile) {
      articles.sort((a, b) => (b.relevance_score || 0) - (a.relevance_score || 0));
    }
    
    return articles;

  } catch (e) {
    Logger.log(`Error fetching news data: ${e.message}`);
    return { error: e.message };
  }
}

/**
 * Generates a relevance score for an article based on user profile.
 * @param {Object} article The article object.
 * @param {Object} userProfile The user's profile.
 * @returns {number} Relevance score between 0 and 100.
 */
function generateRelevanceScore(article, userProfile) {
  let score = 50; // Base score
  
  // Simple keyword matching based on user's interests
  const interests = userProfile.profile_q2_answer.toLowerCase();
  const title = article.title.toLowerCase();
  const summary = (article.summary || '').toLowerCase();
  
  // Check for keyword matches
  const keywords = interests.split(/[,\s]+/).filter(word => word.length > 3);
  keywords.forEach(keyword => {
    if (title.includes(keyword) || summary.includes(keyword)) {
      score += 10;
    }
  });
  
  // Avoid topics the user doesn't like
  const avoidTopics = userProfile.profile_q3_answer.toLowerCase();
  const avoidKeywords = avoidTopics.split(/[,\s]+/).filter(word => word.length > 3);
  avoidKeywords.forEach(keyword => {
    if (title.includes(keyword) || summary.includes(keyword)) {
      score -= 15;
    }
  });
  
  return Math.max(0, Math.min(100, score));
}

/**
 * Generates an AI snippet explaining why an article is relevant to the user.
 * @param {Object} article The article object.
 * @param {Object} userProfile The user's profile.
 * @returns {string} AI-generated relevance explanation.
 */
function generateAISnippet(article, userProfile) {
  const score = generateRelevanceScore(article, userProfile);
  
  if (score >= 80) {
    return "🔥 Highly relevant to your interests and goals!";
  } else if (score >= 60) {
    return "📈 This aligns well with your professional development.";
  } else if (score >= 40) {
    return "💡 Worth a quick read for broader context.";
  } else {
    return "📰 General news that might be of interest.";
  }
}

/**
 * Handles AI chat interactions with personalized persona.
 * @param {Object} chatData Contains message and article context.
 * @returns {Object} AI response with persona-specific messaging.
 */
function handleAIChat(chatData) {
  try {
    const userEmail = Session.getActiveUser().getEmail();
    const userProfile = getUserProfile(userEmail);
    
    if (!userProfile) {
      return { error: 'User profile not found.' };
    }
    
    // Generate AI response based on user's persona preference
    const aiResponse = generateAIResponse(chatData.message, chatData.article, userProfile);
    
    // Award points for engaging in discussion
    awardPoints(userEmail, 5, 'AI Discussion');
    
    return {
      response: aiResponse,
      points_awarded: 5,
      total_points: getUserProfile(userEmail).engagement_points
    };
    
  } catch (e) {
    Logger.log(`Error in AI chat: ${e.message}`);
    return { error: e.message };
  }
}

/**
 * Generates an AI response based on user's persona preference.
 * @param {string} message User's message.
 * @param {Object} article Article context.
 * @param {Object} userProfile User's profile.
 * @returns {string} AI response.
 */
function generateAIResponse(message, article, userProfile) {
  const persona = userProfile.ai_persona_description.toLowerCase();
  
  // Simple persona-based responses
  if (persona.includes('mentor') || persona.includes('teacher')) {
    return `As your mentor, I'd like to help you understand this article better. "${message}" - This is a great question! The key insight here is that ${article.title} represents an important development in your field. What specific aspects would you like to explore further?`;
  } else if (persona.includes('analyst') || persona.includes('expert')) {
    return `From an analytical perspective, "${message}" - This article shows interesting patterns. The ${article.source} coverage suggests ${article.title} has broader implications. Would you like me to break down the key data points?`;
  } else if (persona.includes('friend') || persona.includes('casual')) {
    return `Hey! "${message}" - That's a really good point about ${article.title}. I think this is pretty interesting because it affects things you care about. Want to chat more about what this means for you?`;
  } else {
    return `Thanks for asking about "${message}"! This article about ${article.title} is quite relevant to your interests. The key takeaway is that this development could impact your goals. What's your take on this?`;
  }
}

/**
 * Saves an insight from AI chat with user rating.
 * @param {Object} insightData Contains message, article_id, rating, and comment.
 * @returns {Object} Success or error message.
 */
function saveInsight(insightData) {
  try {
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(SAVED_INSIGHTS_SHEET);
    const userEmail = Session.getActiveUser().getEmail();
    
    const insightId = Utilities.getUuid();
    const timestamp = new Date().toISOString();
    
    const newRow = [
      insightId,
      userEmail,
      insightData.article_id || '',
      insightData.message,
      insightData.rating || 5,
      insightData.comment || '',
      timestamp
    ];
    
    sheet.appendRow(newRow);
    
    // Award points for saving insights
    awardPoints(userEmail, 10, 'Saved Insight');
    
    return { 
      status: 'success',
      insight_id: insightId,
      points_awarded: 10
    };
    
  } catch (e) {
    Logger.log(`Error saving insight: ${e.message}`);
    return { status: 'error', message: e.message };
  }
}

/**
 * Awards points to a user for various actions.
 * @param {string} userEmail User's email.
 * @param {number} points Points to award.
 * @param {string} reason Reason for awarding points.
 */
function awardPoints(userEmail, points, reason) {
  try {
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(USER_PROFILES_SHEET);
    const data = sheet.getDataRange().getValues();
    const headers = data.shift();
    
    // Find user row
    for (let i = 0; i < data.length; i++) {
      if (data[i][0] === userEmail) {
        const currentPoints = parseInt(data[i][5]) || 0; // engagement_points column
        const newPoints = currentPoints + points;
        
        // Update the points
        sheet.getRange(i + 2, 6).setValue(newPoints); // +2 because of 1-indexing and header row
        
        Logger.log(`Awarded ${points} points to ${userEmail} for: ${reason}`);
        break;
      }
    }
  } catch (e) {
    Logger.log(`Error awarding points: ${e.message}`);
  }
}

/**
 * Records article read for engagement tracking.
 * @param {string} articleId The article ID that was read.
 * @returns {Object} Success message with points awarded.
 */
function recordArticleRead(articleId) {
  try {
    const userEmail = Session.getActiveUser().getEmail();
    
    // Award points for reading an article
    awardPoints(userEmail, 3, 'Article Read');
    
    return {
      status: 'success',
      points_awarded: 3,
      total_points: getUserProfile(userEmail).engagement_points
    };
    
  } catch (e) {
    Logger.log(`Error recording article read: ${e.message}`);
    return { status: 'error', message: e.message };
  }
}

/**
 * Gets user's saved insights.
 * @returns {Array} Array of saved insights.
 */
function getSavedInsights() {
  try {
    const userEmail = Session.getActiveUser().getEmail();
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(SAVED_INSIGHTS_SHEET);
    const data = sheet.getDataRange().getValues();
    const headers = data.shift();
    
    const insights = [];
    data.forEach(row => {
      if (row[1] === userEmail) { // user_email column
        const insight = {};
        headers.forEach((header, index) => {
          insight[header] = row[index];
        });
        insights.push(insight);
      }
    });
    
    return insights;
    
  } catch (e) {
    Logger.log(`Error fetching saved insights: ${e.message}`);
    return { error: e.message };
  }
}

// --- Existing Functions ---

/**
 * Includes the content of another file into the main HTML template.
 */
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}
