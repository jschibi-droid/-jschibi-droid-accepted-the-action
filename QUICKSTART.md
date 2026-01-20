# Quick Start Guide

## Setup Steps

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Google Cloud**
   - Enable the following APIs in Google Cloud Console:
     - Google Drive API
     - Google Sheets API
     - Vertex AI API
   
   - Create OAuth 2.0 credentials:
     1. Go to Google Cloud Console > APIs & Services > Credentials
     2. Create OAuth 2.0 Client ID (Desktop application)
     3. Download JSON and save as `credentials.json`
   
   - Set up Application Default Credentials for Vertex AI:
     ```bash
     gcloud auth application-default login
     ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set:
   - `GCP_PROJECT_ID`: Your Google Cloud project ID
   - `DRIVE_FOLDER_ID`: ID of the root Drive folder (from URL)
   - `SHEETS_SPREADSHEET_ID`: ID of the target spreadsheet (from URL)

4. **Verify Setup**
   ```bash
   python setup_check.py
   ```

## Running the Application

### Quick Analysis (Metadata Only)
Fast analysis using only filename metadata:
```bash
python main.py
```

### Full PDF Analysis
Slower but more accurate, downloads and analyzes PDF content:
```bash
python main.py --download-pdfs
```

## Finding IDs

### Google Drive Folder ID
From the Drive folder URL:
```
https://drive.google.com/drive/folders/[FOLDER_ID_HERE]
                                        ^^^^^^^^^^^^^^^^
```

### Google Sheets Spreadsheet ID
From the Sheets URL:
```
https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID_HERE]/edit
                                       ^^^^^^^^^^^^^^^^^^^^^
```

## Common Issues

### "No module named 'google'"
**Solution**: Install dependencies with `pip install -r requirements.txt`

### "Missing required configuration"
**Solution**: Create `.env` file and set required variables (see step 3)

### "Authentication failed"
**Solution**: 
1. Delete `token.json` file
2. Run the application again
3. Complete OAuth flow in browser

### "API quota exceeded"
**Solution**:
1. Reduce `BATCH_SIZE` in `.env`
2. Request quota increase in Google Cloud Console
3. Run during off-peak hours

## Expected Output

The application will:
1. Crawl the specified Drive folder recursively
2. Find all PDF files
3. Extract metadata using regex patterns
4. Use Gemini to extract coupon information
5. Write results to Google Sheets

### Google Sheets Columns
- File ID
- Filename
- Created/Modified timestamps
- Web View Link (to open in Drive)
- Extracted metadata (date, dealership, version, campaign, region, model)
- Coupon information (JSON format)
- Processed timestamp

## Performance Tips

- **For thousands of files**: Use metadata-only mode first
- **Adjust batch size**: Set `BATCH_SIZE` in `.env` (default: 100)
- **Monitor progress**: Check console logs for real-time status
- **API limits**: Respect Google API quotas (see Cloud Console)

## Testing

Run the test suite:
```bash
python -m unittest test_analyzer -v
```

## Support

For issues, check:
1. Application logs (colored console output)
2. Google Cloud Console for API quotas
3. README.md for detailed documentation
