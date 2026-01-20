#!/usr/bin/env python3
"""
Setup script for the Dealership Proof Analyzer.
Helps users set up the environment and verify configuration.
"""
import os
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} not found: {filepath}")
        return False


def check_env_variable(var_name):
    """Check if an environment variable is set."""
    value = os.getenv(var_name)
    if value:
        print(f"✓ {var_name}: Set")
        return True
    else:
        print(f"✗ {var_name}: Not set")
        return False


def main():
    """Run setup checks."""
    print("="*80)
    print("Dealership Proof Analyzer - Setup Verification")
    print("="*80)
    print()
    
    all_checks_passed = True
    
    # Check Python version
    print("Python Version Check:")
    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("  ✓ Python version is 3.8 or higher")
    else:
        print("  ✗ Python version must be 3.8 or higher")
        all_checks_passed = False
    print()
    
    # Check required files
    print("Required Files Check:")
    files_to_check = [
        ('requirements.txt', 'Requirements file'),
        ('.env.example', 'Environment example file'),
        ('config.py', 'Configuration module'),
        ('main.py', 'Main application'),
        ('drive_service.py', 'Drive service module'),
        ('sheets_service.py', 'Sheets service module'),
        ('vertex_ai_service.py', 'Vertex AI service module'),
        ('metadata_extractor.py', 'Metadata extractor module'),
    ]
    
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    print()
    
    # Check for credentials file
    print("Credentials Check:")
    if check_file_exists('credentials.json', 'Google OAuth credentials'):
        print("  ✓ OAuth credentials found")
    else:
        print("  ✗ OAuth credentials not found")
        print("  → Download from Google Cloud Console and save as credentials.json")
        all_checks_passed = False
    print()
    
    # Check for .env file
    print("Environment Configuration Check:")
    if check_file_exists('.env', 'Environment configuration'):
        print("  ✓ Environment file found")
        print("  Checking required variables:")
        
        # Load .env file manually
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
        
        required_vars = [
            'GCP_PROJECT_ID',
            'DRIVE_FOLDER_ID',
            'SHEETS_SPREADSHEET_ID'
        ]
        
        for var in required_vars:
            if not check_env_variable(var):
                all_checks_passed = False
    else:
        print("  ✗ Environment file not found")
        print("  → Copy .env.example to .env and fill in your configuration")
        all_checks_passed = False
    print()
    
    # Check Python packages
    print("Python Packages Check:")
    required_packages = [
        'google-auth',
        'google-api-python-client',
        'google-cloud-aiplatform',
        'python-dotenv',
        'coloredlogs',
        'tenacity'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package}")
            missing_packages.append(package)
            all_checks_passed = False
    
    if missing_packages:
        print()
        print("  Missing packages detected. Install with:")
        print("  pip install -r requirements.txt")
    print()
    
    # Final summary
    print("="*80)
    if all_checks_passed:
        print("✓ All checks passed! You're ready to run the analyzer.")
        print()
        print("To run the analyzer:")
        print("  python main.py")
        print()
        print("For full PDF analysis:")
        print("  python main.py --download-pdfs")
    else:
        print("✗ Some checks failed. Please fix the issues above before running.")
        print()
        print("Setup steps:")
        print("1. Copy .env.example to .env and configure it")
        print("2. Download OAuth credentials from Google Cloud Console")
        print("3. Install required packages: pip install -r requirements.txt")
    print("="*80)
    
    return 0 if all_checks_passed else 1


if __name__ == '__main__':
    sys.exit(main())
