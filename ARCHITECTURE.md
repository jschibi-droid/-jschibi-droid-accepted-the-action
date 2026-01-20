# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Dealership Proof Analyzer                     │
│                          (main.py)                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                   ┌─────────┴─────────┐
                   │   Configuration   │
                   │    (config.py)    │
                   └─────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Google Drive │    │ Vertex AI    │    │Google Sheets │
│   Service    │    │   Service    │    │   Service    │
└──────────────┘    └──────────────┘    └──────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Crawl      │    │   Extract    │    │   Write      │
│   Folders    │───▶│   Coupons    │───▶│   Results    │
└──────────────┘    └──────────────┘    └──────────────┘
        │                    │
        ▼                    │
┌──────────────┐            │
│   Metadata   │────────────┘
│  Extractor   │
└──────────────┘
```

## Component Details

### 1. Main Application (main.py)
**Purpose**: Orchestrates the entire pipeline

**Responsibilities**:
- Initialize all services
- Coordinate data flow
- Handle errors and logging
- Manage CLI interface

**Key Methods**:
- `crawl_drive_folder()`: Start folder traversal
- `process_files()`: Process each PDF
- `write_results_to_sheets()`: Output results
- `run()`: Main execution flow

### 2. Configuration (config.py)
**Purpose**: Centralized configuration management

**Features**:
- Environment variable loading
- Configuration validation
- Default values
- API scope definitions

**Key Settings**:
- Google Cloud project details
- Drive folder ID
- Sheets spreadsheet ID
- Vertex AI model settings
- Application behavior settings

### 3. Google Drive Service (drive_service.py)
**Purpose**: Interface with Google Drive API

**Features**:
- OAuth 2.0 authentication
- Recursive folder crawling
- Pagination handling
- Retry logic with exponential backoff
- File metadata retrieval
- PDF content download

**Key Methods**:
- `crawl_folder_structure()`: Traverse folders
- `list_files_in_folder()`: List folder contents
- `download_file_content()`: Get PDF bytes

**Scale Optimization**:
- Processes thousands of folders
- 1000 files per API call
- Automatic pagination
- Parallel-safe design

### 4. Metadata Extractor (metadata_extractor.py)
**Purpose**: Extract structured data from filenames

**Features**:
- Regex-based pattern matching
- Multiple pattern support per field
- Path-based metadata extraction
- Date parsing and normalization

**Extracted Fields**:
- Date (multiple formats)
- Dealership name
- Version/revision number
- Campaign identifier
- State/region code
- Vehicle model

**Patterns**:
- Date: YYYY-MM-DD, YYYYMMDD, MM-DD-YYYY
- Version: v1, version_2, r3
- Campaign: campaign_ID, SPRING2024
- Region: state_CA, _TX_
- Model: civic, accord, f150, etc.

### 5. Vertex AI Service (vertex_ai_service.py)
**Purpose**: AI-powered coupon extraction

**Features**:
- Gemini 1.5 Flash integration
- Prompt engineering for extraction
- Support for PDF content analysis
- Batch processing capability
- Retry logic for API failures

**Extraction**:
- Coupon offer descriptions
- Expiration dates
- Terms and conditions
- Target vehicles
- Special restrictions

**Output Format**: Structured JSON

### 6. Google Sheets Service (sheets_service.py)
**Purpose**: Write results to spreadsheet

**Features**:
- OAuth 2.0 authentication
- Batch write operations
- Header management
- Append and update support
- Clear range functionality
- Retry logic

**Optimization**:
- Batch writes (default: 100 rows)
- Minimizes API calls
- Efficient quota usage

## Data Flow

### Step 1: Initialization
1. Load configuration from environment
2. Validate required settings
3. Initialize all services
4. Authenticate with Google APIs

### Step 2: Drive Crawl
1. Start at root folder ID
2. List all files and subfolders
3. Handle pagination (1000 items/page)
4. Queue subfolders for processing
5. Collect all PDF files

### Step 3: Metadata Extraction
1. For each PDF file:
   - Extract filename
   - Apply regex patterns
   - Parse dates
   - Extract folder path info
   - Combine all metadata

### Step 4: AI Processing
1. Prepare prompt with metadata
2. Optionally download PDF content
3. Call Vertex AI Gemini
4. Parse JSON response
5. Handle errors/retries

### Step 5: Results Writing
1. Format results as rows
2. Write header to Sheet
3. Batch append data
4. Log progress
5. Handle API limits

## Error Handling Strategy

### Retry Logic
- All API calls use tenacity
- 3 attempts per operation
- Exponential backoff (4-10 seconds)
- Preserves system stability

### Graceful Degradation
- Failed files don't stop pipeline
- Errors logged with context
- Partial results saved
- Progress tracked continuously

### Validation
- Configuration validated at startup
- File IDs verified
- API responses checked
- Data types validated

## Performance Characteristics

### Scalability
- **Folders**: Handles thousands efficiently
- **Files**: Processes at API rate limits
- **Batch Size**: Configurable (default 100)
- **Memory**: Streams data, no full load

### Speed Optimization
- **Metadata-only mode**: Fast analysis
- **Full PDF mode**: Slower but accurate
- **Parallel potential**: Can be added
- **Pagination**: Automatic handling

### API Quotas
- **Drive API**: 1000 requests/100 seconds
- **Sheets API**: 100 requests/100 seconds
- **Vertex AI**: Model-specific limits
- **Monitoring**: Via Cloud Console

## Security Features

### Authentication
- OAuth 2.0 for Drive/Sheets
- Application Default Credentials for Vertex AI
- Secure token storage
- Automatic refresh

### Data Protection
- No secrets in code
- Environment variables for config
- Credentials in .gitignore
- Read-only Drive access

### Dependencies
- No known vulnerabilities
- Regular version updates
- Minimal dependency tree
- Trusted packages only

## Testing Strategy

### Unit Tests
- Metadata extraction patterns
- Date parsing logic
- Service imports
- Configuration validation

### Integration Points
- Google APIs (manual testing)
- End-to-end pipeline (user testing)
- Error scenarios (manual testing)

## Monitoring & Logging

### Log Levels
- **DEBUG**: Detailed operation info
- **INFO**: Progress and milestones
- **WARNING**: Non-fatal issues
- **ERROR**: Operation failures

### Log Output
- Color-coded console
- Timestamps included
- Service context
- Structured messages

### Progress Tracking
- Files processed count
- Folders traversed
- Batch completion
- Time estimates

## Extensibility

### Adding New Metadata Patterns
1. Edit `metadata_extractor.py`
2. Add regex to PATTERNS dict
3. Test with sample files
4. Update EXAMPLES.md

### Custom Processing
1. Subclass services
2. Override methods
3. Inject custom logic
4. Maintain interface

### Additional APIs
1. Create new service module
2. Follow existing pattern
3. Add to main.py
4. Update documentation

## Deployment Considerations

### Environment Requirements
- Python 3.8+
- Internet connectivity
- Google Cloud project
- API credentials

### Resource Needs
- **CPU**: Minimal (I/O bound)
- **Memory**: ~100-500 MB
- **Storage**: Minimal (no local PDFs by default)
- **Network**: Steady connection required

### Production Setup
1. Use service account for auth
2. Set up monitoring/alerting
3. Configure log aggregation
4. Implement retry policies
5. Set API quota alerts

## Maintenance

### Regular Tasks
- Update dependencies
- Monitor API quotas
- Review error logs
- Update regex patterns

### Troubleshooting
- Check setup_check.py
- Review application logs
- Verify API quotas
- Test authentication
- Validate configuration
