// Configuration Constants
const SHEET_ID = '1KBIhQMQFfiSxPXS1-tLBF_efVexGcUBvGJx-leX41og';
const USER_PROFILES_SHEET = 'User_Profiles';
const SAVED_INSIGHTS_SHEET = 'Saved_Insights';
const DASHBOARD_SHEET = 'Dashboard';
const ARTICLES_SHEET = 'Articles';
const LOGS_SHEET = 'Logs';

/**
 * Main entry point for the web app.
 * Implements user authentication and routing logic.
 */
function doGet(e) {
  try {
    setupSheets(); // Ensure required sheets exist
    
    const userEmail = Session.getActiveUser().getEmail();
    
    // Check if user email is available
    if (!userEmail) {
      return createErrorPage('Authentication required. Please sign in with your Google account.');
    }
    
    const userProfile = getUserProfile(userEmail);

    if (userProfile) {
      // User has a profile, show the main dashboard
      return HtmlService.createTemplateFromFile('Index').evaluate()
          .setTitle('Singapore News Intelligence Dashboard')
          .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
          .addMetaTag('viewport', 'width=device-width, initial-scale=1.0');
    } else {
      // New user, show the onboarding survey
      return HtmlService.createTemplateFromFile('Onboarding').evaluate()
          .setTitle('Welcome! Tell Us About Yourself')
          .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
          .addMetaTag('viewport', 'width=device-width, initial-scale=1.0');
    }
  } catch (error) {
    Logger.log(`Error in doGet: ${error.message}`);
    return createErrorPage('Application error. Please try again later.');
  }
}

/**
 * Creates an error page for display
 */
function createErrorPage(message) {
  const template = HtmlService.createTemplate(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>Error</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
          body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
          .error { color: #d93025; font-size: 18px; }
        </style>
      </head>
      <body>
        <h1>Oops! Something went wrong</h1>
        <p class="error">${message}</p>
        <button onclick="window.location.reload()">Try Again</button>
      </body>
    </html>
  `);
  
  return template.evaluate()
    .setTitle('Error')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * Checks if the required sheets exist and creates them with headers if they don't.
 */
function setupSheets() {
  try {
    const spreadsheet = SpreadsheetApp.openById(SHEET_ID);
    
    // Setup User_Profiles sheet
    setupUserProfilesSheet(spreadsheet);
    
    // Setup Saved_Insights sheet
    setupSavedInsightsSheet(spreadsheet);
    
    // Setup other required sheets
    setupArticlesSheet(spreadsheet);
    setupDashboardSheet(spreadsheet);
    setupLogsSheet(spreadsheet);
    
  } catch (error) {
    Logger.log(`Error in setupSheets: ${error.message}`);
    throw new Error('Failed to setup required sheets');
  }
}

/**
 * Setup User_Profiles sheet
 */
function setupUserProfilesSheet(spreadsheet) {
  let sheet = spreadsheet.getSheetByName(USER_PROFILES_SHEET);
  if (!sheet) {
    sheet = spreadsheet.insertSheet(USER_PROFILES_SHEET);
    const headers = [
      'user_email', 
      'profile_q1_answer', 
      'profile_q2_answer', 
      'profile_q3_answer', 
      'ai_persona_description', 
      'engagement_points',
      'created_at',
      'last_active'
    ];
    sheet.appendRow(headers);
    sheet.hideSheet();
    
    // Format header row
    const headerRange = sheet.getRange(1, 1, 1, headers.length);
    headerRange.setFontWeight('bold');
    headerRange.setBackground('#4285F4');
    headerRange.setFontColor('white');
  }
}

/**
 * Setup Saved_Insights sheet
 */
function setupSavedInsightsSheet(spreadsheet) {
  let sheet = spreadsheet.getSheetByName(SAVED_INSIGHTS_SHEET);
  if (!sheet) {
    sheet = spreadsheet.insertSheet(SAVED_INSIGHTS_SHEET);
    const headers = [
      'insight_id', 
      'user_email', 
      'article_id', 
      'saved_message', 
      'user_rating', 
      'user_comment', 
      'timestamp'
    ];
    sheet.appendRow(headers);
    sheet.hideSheet();
    
    // Format header row
    const headerRange = sheet.getRange(1, 1, 1, headers.length);
    headerRange.setFontWeight('bold');
    headerRange.setBackground('#34a853');
    headerRange.setFontColor('white');
  }
}

/**
 * Setup Articles sheet (if it doesn't exist)
 */
function setupArticlesSheet(spreadsheet) {
  let sheet = spreadsheet.getSheetByName(ARTICLES_SHEET);
  if (!sheet) {
    sheet = spreadsheet.insertSheet(ARTICLES_SHEET);
    const headers = [
      'article_id',
      'source',
      'url',
      'discovered_at',
      'title',
      'content',
      'summary',
      'status'
    ];
    sheet.appendRow(headers);
    
    // Format header row
    const headerRange = sheet.getRange(1, 1, 1, headers.length);
    headerRange.setFontWeight('bold');
    headerRange.setBackground('#ea4335');
    headerRange.setFontColor('white');
  }
}

/**
 * Setup Dashboard sheet (if it doesn't exist)
 */
function setupDashboardSheet(spreadsheet) {
  let sheet = spreadsheet.getSheetByName(DASHBOARD_SHEET);
  if (!sheet) {
    sheet = spreadsheet.insertSheet(DASHBOARD_SHEET);
    const headers = [
      'article_id',
      'source',
      'url',
      'discovered_at',
      'title',
      'summary',
      'relevance_score',
      'ai_snippet'
    ];
    sheet.appendRow(headers);
    
    // Format header row
    const headerRange = sheet.getRange(1, 1, 1, headers.length);
    headerRange.setFontWeight('bold');
    headerRange.setBackground('#1a73e8');
    headerRange.setFontColor('white');
    
    // Add sample data for testing
    const sampleData = [
      [
        'sample_001',
        'Channel NewsAsia',
        'https://www.channelnewsasia.com/singapore/sample-article',
        new Date().toISOString(),
        'Sample Singapore News Article',
        'This is a sample news article for testing the dashboard functionality.',
        0.85,
        'This article is relevant because it discusses Singapore\'s latest developments.'
      ]
    ];
    
    if (sampleData.length > 0) {
      sheet.getRange(2, 1, sampleData.length, headers.length).setValues(sampleData);
    }
  }
}

/**
 * Setup Logs sheet (if it doesn't exist)
 */
function setupLogsSheet(spreadsheet) {
  let sheet = spreadsheet.getSheetByName(LOGS_SHEET);
  if (!sheet) {
    sheet = spreadsheet.insertSheet(LOGS_SHEET);
    const headers = [
      'timestamp',
      'level',
      'event',
      'duration_seconds',
      'details'
    ];
    sheet.appendRow(headers);
    
    // Format header row
    const headerRange = sheet.getRange(1, 1, 1, headers.length);
    headerRange.setFontWeight('bold');
    headerRange.setBackground('#f9ab00');
    headerRange.setFontColor('white');
  }
}

/**
 * Retrieves a user's profile from the User_Profiles sheet.
 * @param {string} email The user's email address.
 * @returns {Object|null} The user profile object or null if not found.
 */
function getUserProfile(email) {
  try {
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(USER_PROFILES_SHEET);
    const data = sheet.getDataRange().getValues();
    
    if (data.length <= 1) {
      return null; // No data besides headers
    }
    
    const headers = data.shift();
    
    for (let i = 0; i < data.length; i++) {
      if (data[i][0] === email) { // email is in the first column
        let profile = {};
        headers.forEach((header, index) => {
          profile[header] = data[i][index];
        });
        
        // Update last active timestamp
        updateUserLastActive(email);
        
        return profile;
      }
    }
    return null;
  } catch (error) {
    Logger.log(`Error getting user profile: ${error.message}`);
    return null;
  }
}

/**
 * Updates the user's last active timestamp
 */
function updateUserLastActive(email) {
  try {
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(USER_PROFILES_SHEET);
    const data = sheet.getDataRange().getValues();
    const headers = data.shift();
    const lastActiveIndex = headers.indexOf('last_active');
    
    if (lastActiveIndex === -1) return; // Column doesn't exist
    
    for (let i = 0; i < data.length; i++) {
      if (data[i][0] === email) {
        sheet.getRange(i + 2, lastActiveIndex + 1).setValue(new Date());
        break;
      }
    }
  } catch (error) {
    Logger.log(`Error updating last active: ${error.message}`);
  }
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
    
    if (!userEmail) {
      return { status: 'error', message: 'User authentication required.' };
    }
    
    // Check if user already exists to prevent duplicates
    if (getUserProfile(userEmail)) {
      return { status: 'error', message: 'User profile already exists.' };
    }
    
    // Validate profile data
    if (!profileData.q1 || !profileData.q2 || !profileData.q3 || !profileData.q4) {
      return { status: 'error', message: 'All questions must be answered.' };
    }
    
    const now = new Date();
    const newRow = [
      userEmail,
      profileData.q1,
      profileData.q2,
      profileData.q3,
      profileData.q4,
      0, // Initial engagement points
      now, // created_at
      now  // last_active
    ];
    
    sheet.appendRow(newRow);
    
    // Log the profile creation
    logEvent('INFO', 'USER_PROFILE_CREATED', 0, `New user profile created for ${userEmail}`);
    
    return { status: 'success' };
  } catch (error) {
    Logger.log(`Error saving user profile: ${error.message}`);
    return { status: 'error', message: 'Failed to save profile. Please try again.' };
  }
}

/**
 * Logs events to the Logs sheet
 */
function logEvent(level, event, duration, details) {
  try {
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(LOGS_SHEET);
    const logRow = [
      new Date(),
      level,
      event,
      duration,
      details
    ];
    sheet.appendRow(logRow);
  } catch (error) {
    Logger.log(`Error logging event: ${error.message}`);
  }
}

/**
 * Includes the content of another file into the main HTML template.
 */
function include(filename) {
  try {
    return HtmlService.createHtmlOutputFromFile(filename).getContent();
  } catch (error) {
    Logger.log(`Error including file ${filename}: ${error.message}`);
    return `<!-- Error loading ${filename} -->`;
  }
}

/**
 * Fetches news data from the 'Dashboard' tab of the Google Sheet.
 * Eventually this will be personalized based on user profile.
 */
function getNewsData() {
  try {
    const startTime = new Date().getTime();
    const spreadsheet = SpreadsheetApp.openById(SHEET_ID);
    const sheet = spreadsheet.getSheetByName(DASHBOARD_SHEET);
    
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
    
    // Log successful data fetch
    const duration = (new Date().getTime() - startTime) / 1000;
    const userEmail = Session.getActiveUser().getEmail();
    logEvent('INFO', 'NEWS_DATA_FETCHED', duration, `Fetched ${articles.length} articles for ${userEmail}`);
    
    return articles;

  } catch (error) {
    Logger.log(`Error fetching news data: ${error.message}`);
    logEvent('ERROR', 'NEWS_DATA_FETCH_FAILED', 0, error.message);
    return { error: error.message };
  }
}

/**
 * Get user engagement statistics
 */
function getUserEngagementStats() {
  try {
    const userEmail = Session.getActiveUser().getEmail();
    const profile = getUserProfile(userEmail);
    
    if (!profile) {
      return { error: 'User profile not found' };
    }
    
    return {
      engagement_points: profile.engagement_points || 0,
      created_at: profile.created_at,
      last_active: profile.last_active
    };
  } catch (error) {
    Logger.log(`Error getting engagement stats: ${error.message}`);
    return { error: error.message };
  }
}

/**
 * Save user insight (for future AI chat feature)
 */
function saveUserInsight(articleId, message, rating, comment) {
  try {
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(SAVED_INSIGHTS_SHEET);
    const userEmail = Session.getActiveUser().getEmail();
    
    const insightId = `insight_${new Date().getTime()}`;
    const newRow = [
      insightId,
      userEmail,
      articleId,
      message,
      rating,
      comment,
      new Date()
    ];
    
    sheet.appendRow(newRow);
    
    // Award engagement points
    updateEngagementPoints(userEmail, 10);
    
    return { status: 'success', insight_id: insightId };
  } catch (error) {
    Logger.log(`Error saving insight: ${error.message}`);
    return { status: 'error', message: error.message };
  }
}

/**
 * Update user engagement points
 */
function updateEngagementPoints(email, points) {
  try {
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(USER_PROFILES_SHEET);
    const data = sheet.getDataRange().getValues();
    const headers = data.shift();
    const pointsIndex = headers.indexOf('engagement_points');
    
    if (pointsIndex === -1) return;
    
    for (let i = 0; i < data.length; i++) {
      if (data[i][0] === email) {
        const currentPoints = data[i][pointsIndex] || 0;
        sheet.getRange(i + 2, pointsIndex + 1).setValue(currentPoints + points);
        break;
      }
    }
  } catch (error) {
    Logger.log(`Error updating engagement points: ${error.message}`);
  }
}
