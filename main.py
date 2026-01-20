"""
Main application for Dealership Proof Analyzer.

This application crawls Google Drive for Direct Mail PDF proofs,
extracts metadata, uses Vertex AI to extract coupon offers,
and logs results to Google Sheets.
"""
import logging
import sys
import json
from datetime import datetime
from typing import List, Dict
import coloredlogs

from config import Config
from drive_service import GoogleDriveService
from sheets_service import GoogleSheetsService
from vertex_ai_service import VertexAIService
from metadata_extractor import MetadataExtractor

# Configure logging
coloredlogs.install(
    level=Config.LOG_LEVEL,
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DealershipProofAnalyzer:
    """Main application class for analyzing dealership proof documents."""
    
    def __init__(self):
        """Initialize the analyzer with all required services."""
        logger.info("Initializing Dealership Proof Analyzer...")
        
        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
        
        # Initialize services
        self.drive_service = GoogleDriveService(
            credentials_file=Config.DRIVE_CREDENTIALS_FILE,
            token_file=Config.DRIVE_TOKEN_FILE,
            scopes=Config.SCOPES
        )
        
        self.sheets_service = GoogleSheetsService(
            credentials_file=Config.DRIVE_CREDENTIALS_FILE,
            token_file=Config.DRIVE_TOKEN_FILE,
            scopes=Config.SCOPES
        )
        
        self.vertex_ai_service = VertexAIService(
            project_id=Config.PROJECT_ID,
            location=Config.LOCATION,
            model_name=Config.VERTEX_AI_MODEL
        )
        
        self.metadata_extractor = MetadataExtractor()
        
        logger.info("All services initialized successfully")
    
    def crawl_drive_folder(self) -> List[Dict]:
        """
        Crawl the configured Google Drive folder for PDF files.
        
        Returns:
            List of file metadata dictionaries
        """
        logger.info(f"Starting crawl of Drive folder: {Config.DRIVE_FOLDER_ID}")
        
        files = self.drive_service.crawl_folder_structure(
            root_folder_id=Config.DRIVE_FOLDER_ID,
            pdf_only=True
        )
        
        logger.info(f"Found {len(files)} PDF files")
        return files
    
    def process_files(self, files: List[Dict], download_pdfs: bool = False) -> List[Dict]:
        """
        Process files to extract metadata and coupon information.
        
        Args:
            files: List of file metadata from Google Drive
            download_pdfs: If True, download PDF content for full analysis
            
        Returns:
            List of processed results
        """
        logger.info(f"Processing {len(files)} files...")
        results = []
        
        for idx, file_info in enumerate(files):
            try:
                logger.info(f"Processing file {idx + 1}/{len(files)}: {file_info['name']}")
                
                # Extract metadata from filename/path
                metadata = self.metadata_extractor.extract_all_metadata(file_info)
                
                # Prepare data for Vertex AI
                file_data = {
                    'filename': file_info['name'],
                    'metadata': metadata
                }
                
                # Optionally download PDF content for full analysis
                if download_pdfs:
                    try:
                        pdf_content = self.drive_service.download_file_content(file_info['id'])
                        file_data['pdf_content'] = pdf_content
                        logger.debug(f"Downloaded PDF content for {file_info['name']}")
                    except Exception as e:
                        logger.warning(f"Could not download PDF {file_info['name']}: {e}")
                
                # Extract coupon information using Vertex AI
                coupon_info = self.vertex_ai_service.extract_coupon_info(
                    filename=file_data['filename'],
                    metadata=file_data['metadata'],
                    pdf_content=file_data.get('pdf_content'),
                    temperature=Config.VERTEX_AI_TEMPERATURE,
                    max_output_tokens=Config.VERTEX_AI_MAX_OUTPUT_TOKENS
                )
                
                # Combine all information
                result = {
                    'file_id': file_info['id'],
                    'filename': file_info['name'],
                    'created_time': file_info.get('createdTime', ''),
                    'modified_time': file_info.get('modifiedTime', ''),
                    'web_view_link': file_info.get('webViewLink', ''),
                    'metadata': metadata,
                    'coupon_info': coupon_info,
                    'processed_time': datetime.now().isoformat()
                }
                
                results.append(result)
                
                # Log progress periodically
                if (idx + 1) % 10 == 0:
                    logger.info(f"Processed {idx + 1}/{len(files)} files")
                
            except Exception as e:
                logger.error(f"Error processing file {file_info.get('name', 'unknown')}: {e}")
                # Continue with next file
                continue
        
        logger.info(f"Successfully processed {len(results)} files")
        return results
    
    def write_results_to_sheets(self, results: List[Dict]):
        """
        Write results to Google Sheets.
        
        Args:
            results: List of processed results
        """
        if not results:
            logger.warning("No results to write to Google Sheets")
            return
        
        logger.info(f"Writing {len(results)} results to Google Sheets...")
        
        # Prepare header row
        headers = [
            'File ID',
            'Filename',
            'Created Time',
            'Modified Time',
            'Web View Link',
            'Date',
            'Dealership',
            'Version',
            'Campaign',
            'Region',
            'Model',
            'Coupon Info',
            'Processed Time'
        ]
        
        # Write header
        self.sheets_service.write_header(
            spreadsheet_id=Config.SHEETS_SPREADSHEET_ID,
            range_name=Config.SHEETS_RANGE,
            headers=headers
        )
        
        # Prepare data rows
        rows = []
        for result in results:
            metadata = result.get('metadata', {})
            
            # Parse coupon info if it's JSON
            coupon_info_str = result.get('coupon_info', '')
            try:
                coupon_info_json = json.loads(coupon_info_str)
                coupon_info_display = json.dumps(coupon_info_json, indent=2)
            except:
                coupon_info_display = coupon_info_str
            
            row = [
                result.get('file_id', ''),
                result.get('filename', ''),
                result.get('created_time', ''),
                result.get('modified_time', ''),
                result.get('web_view_link', ''),
                metadata.get('date', ''),
                metadata.get('dealership', ''),
                metadata.get('version', ''),
                metadata.get('campaign', ''),
                metadata.get('region', ''),
                metadata.get('model', ''),
                coupon_info_display,
                result.get('processed_time', '')
            ]
            rows.append(row)
        
        # Write data in batches
        batch_size = Config.BATCH_SIZE
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            self.sheets_service.append_rows(
                spreadsheet_id=Config.SHEETS_SPREADSHEET_ID,
                range_name=Config.SHEETS_RANGE,
                rows=batch
            )
            logger.info(f"Written batch {i // batch_size + 1}: {len(batch)} rows")
        
        logger.info("Successfully written all results to Google Sheets")
    
    def run(self, download_pdfs: bool = False):
        """
        Run the complete analysis pipeline.
        
        Args:
            download_pdfs: If True, download PDF content for full analysis
        """
        try:
            logger.info("="*80)
            logger.info("Starting Dealership Proof Analyzer")
            logger.info("="*80)
            
            # Step 1: Crawl Google Drive
            files = self.crawl_drive_folder()
            
            if not files:
                logger.warning("No PDF files found in the specified Drive folder")
                return
            
            # Step 2: Process files
            results = self.process_files(files, download_pdfs=download_pdfs)
            
            # Step 3: Write results to Google Sheets
            self.write_results_to_sheets(results)
            
            logger.info("="*80)
            logger.info("Analysis complete!")
            logger.info(f"Total files processed: {len(results)}")
            logger.info("="*80)
            
        except KeyboardInterrupt:
            logger.warning("Analysis interrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Fatal error during analysis: {e}", exc_info=True)
            sys.exit(1)


def main():
    """Main entry point for the application."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze Direct Mail PDF proofs from Google Drive'
    )
    parser.add_argument(
        '--download-pdfs',
        action='store_true',
        help='Download PDF content for full analysis (slower but more accurate)'
    )
    
    args = parser.parse_args()
    
    analyzer = DealershipProofAnalyzer()
    analyzer.run(download_pdfs=args.download_pdfs)


if __name__ == '__main__':
    main()
