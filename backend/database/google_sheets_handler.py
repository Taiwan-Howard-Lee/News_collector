import gspread
import logging
import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from typing import Dict

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the scope for Google Sheets and Drive API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'config/credentials.json'

# Get Google Sheet ID from environment variables
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

def get_gspread_client():
    """
    Authenticates with the Google API using service account credentials
    and returns a gspread client instance.
    """
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        logging.info("Successfully authenticated with Google Sheets API.")
        return client
    except FileNotFoundError:
        logging.error(f"CRITICAL: The credential file was not found at '{SERVICE_ACCOUNT_FILE}'.")
        logging.error("Please make sure you have created a service account and placed the JSON key in the correct path.")
        return None
    except Exception as e:
        logging.error(f"An error occurred during Google API authentication: {e}")
        return None

def insert_article(client: gspread.Client, worksheet_name: str, article_data: Dict):
    """
    Appends a new row to a specific worksheet in the Google Sheet.

    Args:
        client: The authenticated gspread client.
        sheet_name: The name of the Google Sheet.
        worksheet_name: The name of the worksheet (tab) to write to.
        article_data: A dictionary containing the article data.
    """
    if not GOOGLE_SHEET_ID:
        logging.error("CRITICAL: GOOGLE_SHEET_ID is not set in the environment variables.")
        return False
    try:
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        worksheet = spreadsheet.worksheet(worksheet_name)
        
        # Columns: article_id, source, url, discovered_at, title, content, summary
        row_to_insert = [
            article_data.get('article_id', 'N/A'),
            article_data.get('source', 'N/A'),
            article_data.get('url', 'N/A'),
            article_data.get('discovered_at', 'N/A'),
            article_data.get('title', 'N/A'),
            article_data.get('content', 'N/A'),
            article_data.get('summary', 'N/A')
        ]
        
        worksheet.append_row(row_to_insert)
        logging.info(f"Successfully inserted article into spreadsheet: {article_data.get('title')}")
        return True
    except gspread.exceptions.WorksheetNotFound:
        logging.error(f"Worksheet '{worksheet_name}' not found in the spreadsheet.")
        return False
    except gspread.exceptions.SpreadsheetNotFound:
        logging.error(f"Spreadsheet not found. Check the GOOGLE_SHEET_ID and sharing permissions.")
        return False
    except Exception as e:
        logging.error(f"Failed to insert article into Google Sheet: {e}")
        return False

def insert_log(client: gspread.Client, log_data: Dict):
    """
    Appends a new log entry to the 'Logs' worksheet.

    Args:
        client: The authenticated gspread client.
        sheet_name: The name of the Google Sheet.
        log_data: A dictionary containing the log data.
    """
    if not GOOGLE_SHEET_ID:
        logging.error("CRITICAL: GOOGLE_SHEET_ID is not set in the environment variables.")
        return False
    try:
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        worksheet = spreadsheet.worksheet('Logs')
        
        # Columns: timestamp, level, event, duration_seconds, details
        log_entry = [
            log_data.get('timestamp', 'N/A'),
            log_data.get('level', 'INFO'),
            log_data.get('event', 'N/A'),
            log_data.get('duration_seconds', 0),
            log_data.get('details', '')
        ]
        
        worksheet.append_row(log_entry)
        logging.info(f"Successfully inserted log into the spreadsheet.")
        return True
    except gspread.exceptions.WorksheetNotFound:
        logging.error(f"Worksheet 'Logs' not found in the spreadsheet. Please create it.")
        return False
    except gspread.exceptions.SpreadsheetNotFound:
        logging.error(f"Spreadsheet not found. Check the GOOGLE_SHEET_ID and sharing permissions.")
        return False
    except Exception as e:
        logging.error(f"Failed to insert log into Google Sheet: {e}")
        return False
