"""
Configuration module for the Dealership Proof Analyzer.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings for the application."""
    
    # Google Cloud Project Settings
    PROJECT_ID = os.getenv('GCP_PROJECT_ID', '')
    LOCATION = os.getenv('GCP_LOCATION', 'us-central1')
    
    # Google Drive Settings
    DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID', '')
    DRIVE_CREDENTIALS_FILE = os.getenv('DRIVE_CREDENTIALS_FILE', 'credentials.json')
    DRIVE_TOKEN_FILE = os.getenv('DRIVE_TOKEN_FILE', 'token.json')
    
    # Google Sheets Settings
    SHEETS_SPREADSHEET_ID = os.getenv('SHEETS_SPREADSHEET_ID', '')
    SHEETS_RANGE = os.getenv('SHEETS_RANGE', 'Sheet1!A1')
    
    # Vertex AI Settings
    VERTEX_AI_MODEL = os.getenv('VERTEX_AI_MODEL', 'gemini-1.5-flash')
    VERTEX_AI_MAX_OUTPUT_TOKENS = int(os.getenv('VERTEX_AI_MAX_OUTPUT_TOKENS', '2048'))
    VERTEX_AI_TEMPERATURE = float(os.getenv('VERTEX_AI_TEMPERATURE', '0.2'))
    
    # Application Settings
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '5'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '100'))
    
    # Scopes for Google APIs
    SCOPES = [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/spreadsheets'
    ]
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        required_fields = {
            'PROJECT_ID': cls.PROJECT_ID,
            'DRIVE_FOLDER_ID': cls.DRIVE_FOLDER_ID,
            'SHEETS_SPREADSHEET_ID': cls.SHEETS_SPREADSHEET_ID,
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        
        if missing_fields:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing_fields)}. "
                "Please set these in your .env file or environment variables."
            )
