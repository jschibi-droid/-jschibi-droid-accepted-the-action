# Dealership Proof Analyzer

A robust Python application that integrates Google Drive, Vertex AI, and Google Sheets to process Direct Mail PDF proofs at scale.

## Overview

This application crawls massive Google Drive folder structures (thousands of subfolders) containing Direct Mail PDF proofs, extracts metadata using regex patterns, leverages Vertex AI (Gemini 1.5 Flash) to extract specific coupon offers, and logs comprehensive results into a Google Sheet.

## Features

- **Scalable Google Drive Crawler**: Efficiently traverses thousands of subfolders with automatic pagination and retry logic
- **Intelligent Metadata Extraction**: Uses regex patterns to extract dealership info, dates, versions, campaigns, and more from filenames and paths
- **AI-Powered Coupon Extraction**: Leverages Vertex AI's Gemini 1.5 Flash model to extract detailed coupon offers from PDFs
- **Robust Error Handling**: Automatic retries with exponential backoff for all API calls
- **Google Sheets Integration**: Batch writes results with structured data for easy analysis
- **Flexible Processing**: Options for metadata-only analysis or full PDF content analysis
- **Comprehensive Logging**: Detailed logging with color-coded output for monitoring

## Architecture

The application consists of several modular components:

- `main.py`: Main application orchestrator
- `config.py`: Configuration management with environment variables
- `drive_service.py`: Google Drive API integration
- `sheets_service.py`: Google Sheets API integration
- `vertex_ai_service.py`: Vertex AI (Gemini) integration
- `metadata_extractor.py`: Regex-based metadata extraction

## Prerequisites

- Python 3.8+
- Google Cloud Project with:
  - Vertex AI API enabled
  - Google Drive API enabled
  - Google Sheets API enabled
- OAuth 2.0 credentials for Google Drive and Sheets
- Google Cloud service account (for Vertex AI)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd -jschibi-droid-accepted-the-action
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Cloud credentials:
   - Download OAuth 2.0 credentials from Google Cloud Console and save as `credentials.json`
   - Set up Application Default Credentials for Vertex AI:
     ```bash
     gcloud auth application-default login
     ```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

Create a `.env` file with the following settings:

```bash
# Google Cloud Project Settings
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1

# Google Drive Settings
DRIVE_FOLDER_ID=your-drive-folder-id
DRIVE_CREDENTIALS_FILE=credentials.json
DRIVE_TOKEN_FILE=token.json

# Google Sheets Settings
SHEETS_SPREADSHEET_ID=your-spreadsheet-id
SHEETS_RANGE=Sheet1!A1

# Vertex AI Settings
VERTEX_AI_MODEL=gemini-1.5-flash
VERTEX_AI_MAX_OUTPUT_TOKENS=2048
VERTEX_AI_TEMPERATURE=0.2

# Application Settings
MAX_WORKERS=5
LOG_LEVEL=INFO
BATCH_SIZE=100
```

### Configuration Parameters

- `GCP_PROJECT_ID`: Your Google Cloud project ID
- `GCP_LOCATION`: Google Cloud region (default: us-central1)
- `DRIVE_FOLDER_ID`: ID of the root Google Drive folder to crawl
- `SHEETS_SPREADSHEET_ID`: ID of the Google Sheet to write results to
- `VERTEX_AI_MODEL`: Gemini model to use (default: gemini-1.5-flash)
- `VERTEX_AI_TEMPERATURE`: Model temperature (0.0-1.0, lower = more deterministic)
- `BATCH_SIZE`: Number of rows to write to Sheets in each batch
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Usage

### Basic Usage (Metadata-only Analysis)

Process files using only filename/path metadata:

```bash
python main.py
```

This is faster and suitable when filenames contain sufficient information.

### Full PDF Analysis

Download and analyze actual PDF content:

```bash
python main.py --download-pdfs
```

This is slower but more accurate as it processes the actual PDF content with Gemini.

## Output

Results are written to Google Sheets with the following columns:

- **File ID**: Google Drive file ID
- **Filename**: Name of the PDF file
- **Created Time**: File creation timestamp
- **Modified Time**: File modification timestamp
- **Web View Link**: Link to view file in Google Drive
- **Date**: Extracted date from filename
- **Dealership**: Extracted dealership name
- **Version**: Proof version number
- **Campaign**: Campaign identifier
- **Region**: State/region code
- **Model**: Vehicle model information
- **Coupon Info**: JSON-formatted coupon offer details
- **Processed Time**: When the file was processed

## Metadata Extraction Patterns

The application uses regex to extract:

- **Dates**: YYYY-MM-DD, MM-DD-YYYY, YYYYMMDD formats
- **Dealership**: From filenames and folder paths
- **Versions**: proof_v1, version_2, r1, etc.
- **Campaigns**: campaign_SPRING2024, promo_FALL23, etc.
- **Regions**: State codes (CA, NY, TX, etc.)
- **Models**: Common vehicle models (Civic, F-150, etc.)

## Coupon Information Extraction

Gemini extracts structured information including:

- Offer descriptions (e.g., "$500 off", "0% APR for 60 months")
- Expiration dates
- Terms and conditions
- Target vehicle models
- Special requirements or restrictions

## Error Handling

The application includes robust error handling:

- **Automatic Retries**: All API calls retry up to 3 times with exponential backoff
- **Graceful Degradation**: Continues processing remaining files if one fails
- **Comprehensive Logging**: All errors are logged with context
- **Validation**: Configuration validation before processing starts

## Performance Considerations

For processing thousands of files:

- Use metadata-only mode (`python main.py`) for initial analysis
- Adjust `BATCH_SIZE` to optimize Sheets API usage
- Monitor API quotas in Google Cloud Console
- Consider running during off-peak hours for large batches

## Troubleshooting

### Authentication Issues

If you encounter authentication errors:

```bash
# Re-authenticate with Google Cloud
gcloud auth application-default login

# Remove token file to re-authorize
rm token.json
python main.py
```

### API Quota Errors

If you hit API quotas:

- Reduce `BATCH_SIZE` in configuration
- Add delays between batches
- Request quota increases in Google Cloud Console

### PDF Processing Errors

If PDF processing fails:

- Try metadata-only mode first
- Check that PDFs are not corrupted
- Verify Vertex AI API is enabled and has quota

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Support

For issues and questions, please open a GitHub issue.
