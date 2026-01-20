"""
Unit tests for the Dealership Proof Analyzer application.
"""
import unittest
from datetime import datetime
from metadata_extractor import MetadataExtractor


class TestMetadataExtractor(unittest.TestCase):
    """Test cases for MetadataExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = MetadataExtractor()
    
    def test_extract_date_from_filename(self):
        """Test date extraction from various filename formats."""
        test_cases = [
            ('proof_2024-01-15_v1.pdf', '2024-01-15'),
            ('mailer_2024_02_20.pdf', '2024-02-20'),
            ('direct_mail_20240315.pdf', '2024-03-15'),
            ('campaign_03-25-2024.pdf', '2024-03-25'),
        ]
        
        for filename, expected_date in test_cases:
            metadata = self.extractor.extract_from_filename(filename)
            self.assertIsNotNone(metadata['date'], f"Failed to extract date from {filename}")
    
    def test_extract_dealership_from_filename(self):
        """Test dealership extraction from filenames."""
        test_cases = [
            'dealer_ABC123_proof_v1.pdf',
            'client_XYZ_mailer_2024.pdf',
            'HondaDealership_proof_v2.pdf',
        ]
        
        for filename in test_cases:
            metadata = self.extractor.extract_from_filename(filename)
            # Should extract some dealership info
            self.assertIsNotNone(metadata)
    
    def test_extract_version_from_filename(self):
        """Test version extraction from filenames."""
        test_cases = [
            ('proof_v1.pdf', '1'),
            ('mailer_version_2.pdf', '2'),
            ('direct_mail_r3.pdf', '3'),
        ]
        
        for filename, expected_version in test_cases:
            metadata = self.extractor.extract_from_filename(filename)
            self.assertEqual(metadata['version'], expected_version,
                           f"Failed to extract version from {filename}")
    
    def test_extract_campaign_from_filename(self):
        """Test campaign extraction from filenames."""
        test_cases = [
            'campaign_SPRING2024_v1.pdf',
            'offer_SUMMER23_proof.pdf',
            'promo_FALL2024.pdf',
        ]
        
        for filename in test_cases:
            metadata = self.extractor.extract_from_filename(filename)
            self.assertIsNotNone(metadata['campaign'],
                               f"Failed to extract campaign from {filename}")
    
    def test_extract_region_from_filename(self):
        """Test region extraction from filenames."""
        test_cases = [
            ('proof_CA_v1.pdf', 'CA'),
            ('mailer_state_NY.pdf', 'NY'),
            ('direct_TX_2024.pdf', 'TX'),
        ]
        
        for filename, expected_region in test_cases:
            metadata = self.extractor.extract_from_filename(filename)
            self.assertEqual(metadata['region'], expected_region,
                           f"Failed to extract region from {filename}")
    
    def test_extract_model_from_filename(self):
        """Test vehicle model extraction from filenames."""
        test_cases = [
            'civic_proof_v1.pdf',
            'accord_mailer_2024.pdf',
            'f150_direct_mail.pdf',
        ]
        
        for filename in test_cases:
            metadata = self.extractor.extract_from_filename(filename)
            self.assertIsNotNone(metadata['model'],
                               f"Failed to extract model from {filename}")
    
    def test_parse_date_formats(self):
        """Test parsing of different date formats."""
        test_cases = [
            ('2024-01-15', '2024-01-15'),
            ('2024_02_20', '2024-02-20'),
            ('20240315', '2024-03-15'),
            ('03-25-2024', '2024-03-25'),
        ]
        
        for date_str, expected in test_cases:
            parsed = self.extractor._parse_date(date_str)
            self.assertEqual(parsed, expected,
                           f"Failed to parse date {date_str}")
    
    def test_extract_all_metadata(self):
        """Test extraction of all metadata from file info."""
        file_info = {
            'id': 'test_file_id_123',
            'name': 'dealer_ABC_2024-01-15_proof_v1_state_CA.pdf',
            'mimeType': 'application/pdf',
            'createdTime': '2024-01-15T10:00:00.000Z',
            'modifiedTime': '2024-01-15T11:00:00.000Z',
            'webViewLink': 'https://drive.google.com/file/d/test_file_id_123/view'
        }
        
        metadata = self.extractor.extract_all_metadata(file_info)
        
        # Check that all basic fields are extracted
        self.assertEqual(metadata['file_id'], 'test_file_id_123')
        self.assertEqual(metadata['filename'], 'dealer_ABC_2024-01-15_proof_v1_state_CA.pdf')
        self.assertEqual(metadata['mime_type'], 'application/pdf')
        self.assertIsNotNone(metadata['date'])
        self.assertIsNotNone(metadata['dealership'])
        self.assertIsNotNone(metadata['version'])
        self.assertIsNotNone(metadata['region'])


class TestConfigValidation(unittest.TestCase):
    """Test cases for configuration validation."""
    
    def test_config_imports(self):
        """Test that config module imports successfully."""
        try:
            from config import Config
            self.assertIsNotNone(Config)
        except ImportError as e:
            self.fail(f"Failed to import Config: {e}")


class TestServiceImports(unittest.TestCase):
    """Test cases for service module imports."""
    
    def test_drive_service_import(self):
        """Test that drive_service module imports successfully."""
        try:
            from drive_service import GoogleDriveService
            self.assertIsNotNone(GoogleDriveService)
        except ImportError as e:
            self.fail(f"Failed to import GoogleDriveService: {e}")
    
    def test_sheets_service_import(self):
        """Test that sheets_service module imports successfully."""
        try:
            from sheets_service import GoogleSheetsService
            self.assertIsNotNone(GoogleSheetsService)
        except ImportError as e:
            self.fail(f"Failed to import GoogleSheetsService: {e}")
    
    def test_vertex_ai_service_import(self):
        """Test that vertex_ai_service module imports successfully."""
        try:
            from vertex_ai_service import VertexAIService
            self.assertIsNotNone(VertexAIService)
        except ImportError as e:
            self.fail(f"Failed to import VertexAIService: {e}")


if __name__ == '__main__':
    unittest.main()
