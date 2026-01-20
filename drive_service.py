"""
Google Drive service for crawling folder structures and accessing PDF files.
"""
import logging
import os
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class GoogleDriveService:
    """Service for interacting with Google Drive API."""
    
    def __init__(self, credentials_file: str, token_file: str, scopes: List[str]):
        """
        Initialize Google Drive service.
        
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
        """Authenticate with Google Drive API."""
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
        
        self.service = build('drive', 'v3', credentials=creds)
        logger.info("Successfully authenticated with Google Drive API")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def list_files_in_folder(
        self, 
        folder_id: str, 
        mime_type: Optional[str] = None,
        page_token: Optional[str] = None
    ) -> Dict:
        """
        List files in a specific folder.
        
        Args:
            folder_id: ID of the folder to list files from
            mime_type: Optional MIME type filter (e.g., 'application/pdf')
            page_token: Token for pagination
            
        Returns:
            Dictionary with 'files' list and 'nextPageToken' if more results exist
        """
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            if mime_type:
                query += f" and mimeType='{mime_type}'"
            
            results = self.service.files().list(
                q=query,
                pageSize=1000,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, mimeType, parents, createdTime, modifiedTime)"
            ).execute()
            
            return results
        except HttpError as error:
            logger.error(f"Error listing files in folder {folder_id}: {error}")
            raise
    
    def crawl_folder_structure(
        self, 
        root_folder_id: str, 
        pdf_only: bool = True
    ) -> List[Dict]:
        """
        Recursively crawl folder structure to find all PDF files.
        
        Args:
            root_folder_id: ID of the root folder to start crawling
            pdf_only: If True, only return PDF files
            
        Returns:
            List of file metadata dictionaries
        """
        all_files = []
        folders_to_process = [root_folder_id]
        processed_folders = set()
        
        logger.info(f"Starting folder crawl from root: {root_folder_id}")
        
        while folders_to_process:
            current_folder = folders_to_process.pop(0)
            
            if current_folder in processed_folders:
                continue
            
            processed_folders.add(current_folder)
            logger.info(f"Processing folder: {current_folder} ({len(processed_folders)} folders processed)")
            
            page_token = None
            while True:
                try:
                    results = self.list_files_in_folder(current_folder, page_token=page_token)
                    files = results.get('files', [])
                    
                    for file in files:
                        mime_type = file.get('mimeType', '')
                        
                        # If it's a folder, add to processing queue
                        if mime_type == 'application/vnd.google-apps.folder':
                            folders_to_process.append(file['id'])
                        # If it's a PDF (or any file if pdf_only is False), add to results
                        elif not pdf_only or mime_type == 'application/pdf':
                            all_files.append(file)
                            logger.debug(f"Found file: {file['name']}")
                    
                    page_token = results.get('nextPageToken')
                    if not page_token:
                        break
                        
                except HttpError as error:
                    logger.error(f"Error processing folder {current_folder}: {error}")
                    break
        
        logger.info(f"Crawl complete. Found {len(all_files)} files in {len(processed_folders)} folders")
        return all_files
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_file_metadata(self, file_id: str) -> Dict:
        """
        Get detailed metadata for a specific file.
        
        Args:
            file_id: ID of the file
            
        Returns:
            File metadata dictionary
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, parents, createdTime, modifiedTime, size, webViewLink"
            ).execute()
            return file
        except HttpError as error:
            logger.error(f"Error getting file metadata for {file_id}: {error}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def download_file_content(self, file_id: str) -> bytes:
        """
        Download file content.
        
        Args:
            file_id: ID of the file to download
            
        Returns:
            File content as bytes
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_content = request.execute()
            return file_content
        except HttpError as error:
            logger.error(f"Error downloading file {file_id}: {error}")
            raise
