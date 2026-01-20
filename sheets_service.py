"""
Google Sheets service for writing results.
"""
import logging
from typing import List, Dict, Any
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential
import os

logger = logging.getLogger(__name__)


class GoogleSheetsService:
    """Service for interacting with Google Sheets API."""
    
    def __init__(self, credentials_file: str, token_file: str, scopes: List[str]):
        """
        Initialize Google Sheets service.
        
        Args:
            credentials_file: Path to credentials.json file
            token_file: Path to token.json file for storing auth tokens
            scopes: List of OAuth scopes required
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API."""
        creds = None
        
        # Load saved credentials if they exist
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        
        # If credentials are invalid or don't exist, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('sheets', 'v4', credentials=creds)
        logger.info("Successfully authenticated with Google Sheets API")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def write_header(self, spreadsheet_id: str, range_name: str, headers: List[str]):
        """
        Write header row to spreadsheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to write to (e.g., 'Sheet1!A1')
            headers: List of header values
        """
        try:
            body = {
                'values': [headers]
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Header written: {result.get('updatedCells')} cells updated")
            return result
        except HttpError as error:
            logger.error(f"Error writing header: {error}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def append_rows(self, spreadsheet_id: str, range_name: str, rows: List[List[Any]]):
        """
        Append rows to spreadsheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to append to (e.g., 'Sheet1!A1')
            rows: List of rows, where each row is a list of values
        """
        try:
            body = {
                'values': rows
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            logger.info(f"Appended {len(rows)} rows: {result.get('updates', {}).get('updatedCells')} cells updated")
            return result
        except HttpError as error:
            logger.error(f"Error appending rows: {error}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def batch_update_rows(self, spreadsheet_id: str, range_name: str, rows: List[List[Any]]):
        """
        Batch update rows in spreadsheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to update (e.g., 'Sheet1!A2:Z1000')
            rows: List of rows, where each row is a list of values
        """
        try:
            body = {
                'values': rows
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Updated {len(rows)} rows: {result.get('updatedCells')} cells updated")
            return result
        except HttpError as error:
            logger.error(f"Error batch updating rows: {error}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def clear_range(self, spreadsheet_id: str, range_name: str):
        """
        Clear a range in the spreadsheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to clear (e.g., 'Sheet1!A1:Z1000')
        """
        try:
            result = self.service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            logger.info(f"Cleared range: {range_name}")
            return result
        except HttpError as error:
            logger.error(f"Error clearing range: {error}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_values(self, spreadsheet_id: str, range_name: str) -> List[List[Any]]:
        """
        Get values from a range in the spreadsheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to get values from (e.g., 'Sheet1!A1:Z1000')
            
        Returns:
            List of rows with values
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            logger.info(f"Retrieved {len(values)} rows from {range_name}")
            return values
        except HttpError as error:
            logger.error(f"Error getting values: {error}")
            raise
