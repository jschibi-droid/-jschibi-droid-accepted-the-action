# Example PDF Filenames and Extracted Metadata

This document shows examples of PDF filenames and what metadata the application extracts from them.

## Example 1: Full Information
**Filename**: `dealer_Toyota_2024-03-15_proof_v2_state_CA.pdf`

**Extracted Metadata**:
- Date: `2024-03-15`
- Dealership: `Toyota`
- Version: `2`
- Region: `CA`

## Example 2: Campaign Information
**Filename**: `Honda_campaign_SPRING2024_proof_v1.pdf`

**Extracted Metadata**:
- Dealership: `Honda`
- Campaign: `SPRING2024`
- Version: `1`

## Example 3: Vehicle Model
**Filename**: `civic_mailer_2024-04-01_v3.pdf`

**Extracted Metadata**:
- Model: `civic`
- Date: `2024-04-01`
- Version: `3`

## Example 4: Multiple Formats
**Filename**: `client_ABC123_20240515_r1_TX.pdf`

**Extracted Metadata**:
- Dealership: `ABC123`
- Date: `2024-05-15` (from `20240515`)
- Version: `1` (from `r1`)
- Region: `TX`

## Example 5: Minimal Information
**Filename**: `proof_2024_06_20.pdf`

**Extracted Metadata**:
- Date: `2024-06-20`

## Supported Patterns

### Date Patterns
- `YYYY-MM-DD`: `2024-03-15`
- `YYYY_MM_DD`: `2024_03_15`
- `YYYYMMDD`: `20240315`
- `MM-DD-YYYY`: `03-15-2024`
- `MM_DD_YYYY`: `03_15_2024`

### Version Patterns
- `v1`, `v2`, `v3`, etc.
- `version_1`, `version_2`, etc.
- `r1`, `r2`, `r3`, etc. (revision)
- `proof_1`, `proof_2`, etc.

### Dealership Patterns
- `dealer_[name]`
- `client_[name]`
- `customer_[name]`
- `[Name]` at start of filename

### Campaign Patterns
- `campaign_[ID]`
- `offer_[ID]`
- `promo_[ID]`
- `[Word][Number]` (e.g., `SPRING2024`, `FALL23`)

### Region Patterns
- `state_[XX]` (e.g., `state_CA`)
- `region_[XX]`
- `_[XX]_` (e.g., `_CA_`, `_NY_`)

### Vehicle Model Patterns
- Common models: `civic`, `accord`, `crv`, `pilot`, `forester`, `outback`, `camry`, `corolla`, `f150`, `silverado`
- Pattern: `model_[name]`
- Pattern: `vehicle_[name]`

## Folder Structure Metadata

The application also extracts metadata from folder paths:

### Example Folder Structure
```
/2024/
  /03_March/
    /California/
      /Toyota/
        dealer_proof_v1.pdf
```

**Additional Extracted Metadata**:
- Year folder: `2024`
- Month folder: `03`
- Dealership from path: `Toyota`

## Tips for Better Metadata Extraction

1. **Use consistent naming**: Follow a standard pattern across all PDFs
2. **Include dates**: Use ISO format (YYYY-MM-DD) for best results
3. **Tag dealerships**: Include dealership name or code in filename
4. **Version numbers**: Use `v1`, `v2` for proof versions
5. **State codes**: Use standard 2-letter state codes
6. **Campaign IDs**: Include campaign identifier for tracking

## Custom Patterns

If your filenames use different patterns, you can modify the regex patterns in `metadata_extractor.py`:

```python
PATTERNS = {
    'date': [
        r'(\d{4}[-_]\d{2}[-_]\d{2})',  # Add your patterns here
    ],
    # ... other patterns
}
```
