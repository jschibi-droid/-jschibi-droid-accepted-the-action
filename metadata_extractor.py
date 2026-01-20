"""
Metadata extractor for Direct Mail PDF proofs.
"""
import re
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extract metadata from PDF filenames and paths using regex patterns."""
    
    # Common patterns for Direct Mail PDF proofs
    PATTERNS = {
        # Date patterns: YYYY-MM-DD, MM-DD-YYYY, YYYYMMDD, etc.
        'date': [
            r'(\d{4}[-_]\d{2}[-_]\d{2})',  # YYYY-MM-DD or YYYY_MM_DD
            r'(\d{2}[-_]\d{2}[-_]\d{4})',  # MM-DD-YYYY or MM_DD_YYYY
            r'(\d{8})',                     # YYYYMMDD
        ],
        # Dealership/Client patterns
        'dealership': [
            r'(?:dealer|client|customer)[-_]?([A-Za-z0-9]+)',
            r'^([A-Za-z]+)[-_](?:proof|mailer|direct)',
        ],
        # Proof/Version patterns
        'version': [
            r'(?:proof|version|v)[-_]?(\d+)',
            r'_v(\d+)',
            r'[-_]r(\d+)',  # revision
        ],
        # Campaign/Offer patterns
        'campaign': [
            r'(?:campaign|offer|promo)[-_]?([A-Za-z0-9]+)',
            r'([A-Za-z]+\d+)',  # e.g., SPRING2024, FALL23
        ],
        # State/Region patterns
        'region': [
            r'(?:state|region)[-_]?([A-Z]{2})',
            r'[-_]([A-Z]{2})[-_]',
        ],
        # Model/Vehicle patterns
        'model': [
            r'(?:model|vehicle)[-_]?([A-Za-z0-9]+)',
            r'(civic|accord|crv|pilot|forester|outback|camry|corolla|f150|silverado)',  # common models
        ],
    }
    
    def __init__(self):
        """Initialize metadata extractor."""
        self.compiled_patterns = {}
        for key, patterns in self.PATTERNS.items():
            self.compiled_patterns[key] = [re.compile(p, re.IGNORECASE) for p in patterns]
    
    def extract_from_filename(self, filename: str) -> Dict:
        """
        Extract metadata from a filename.
        
        Args:
            filename: Name of the PDF file
            
        Returns:
            Dictionary with extracted metadata
        """
        metadata = {
            'filename': filename,
            'date': None,
            'dealership': None,
            'version': None,
            'campaign': None,
            'region': None,
            'model': None,
        }
        
        # Remove file extension
        name_without_ext = filename.rsplit('.', 1)[0]
        
        # Try each pattern type
        for key, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                match = pattern.search(name_without_ext)
                if match:
                    metadata[key] = match.group(1)
                    logger.debug(f"Found {key}: {metadata[key]} in {filename}")
                    break  # Use first match for each category
        
        # Parse date if found
        if metadata['date']:
            metadata['parsed_date'] = self._parse_date(metadata['date'])
        
        return metadata
    
    def extract_from_path(self, file_path: str) -> Dict:
        """
        Extract metadata from a full file path.
        
        Args:
            file_path: Full path to the PDF file
            
        Returns:
            Dictionary with extracted metadata
        """
        # Get filename metadata first
        filename = file_path.split('/')[-1]
        metadata = self.extract_from_filename(filename)
        
        # Add path information
        metadata['full_path'] = file_path
        path_parts = file_path.split('/')
        metadata['path_depth'] = len(path_parts)
        
        # Try to extract additional info from folder names
        for part in path_parts[:-1]:  # Exclude filename
            # Check for year folders
            if re.match(r'^\d{4}$', part):
                metadata['year_folder'] = part
            
            # Check for month folders
            month_match = re.match(r'^(\d{1,2})[-_]?([A-Za-z]+)?$', part)
            if month_match:
                metadata['month_folder'] = month_match.group(1)
            
            # Check for dealership in path
            if not metadata['dealership']:
                for pattern in self.compiled_patterns['dealership']:
                    match = pattern.search(part)
                    if match:
                        metadata['dealership'] = match.group(1)
                        break
        
        return metadata
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse date string into standardized format.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            ISO format date string (YYYY-MM-DD) or None
        """
        # Try different date formats
        formats = [
            '%Y-%m-%d',
            '%Y_%m_%d',
            '%m-%d-%Y',
            '%m_%d_%Y',
            '%Y%m%d',
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def extract_all_metadata(self, file_info: Dict) -> Dict:
        """
        Extract all metadata from file information.
        
        Args:
            file_info: Dictionary with file information (name, parents, etc.)
            
        Returns:
            Dictionary with all extracted metadata
        """
        filename = file_info.get('name', '')
        
        # Start with filename-based extraction
        metadata = self.extract_from_filename(filename)
        
        # Add file info
        metadata['file_id'] = file_info.get('id')
        metadata['mime_type'] = file_info.get('mimeType')
        metadata['created_time'] = file_info.get('createdTime')
        metadata['modified_time'] = file_info.get('modifiedTime')
        metadata['web_view_link'] = file_info.get('webViewLink')
        
        return metadata
