# Downloading School Data from ISTAT

This directory contains scripts to download and process school data from ISTAT (Italian National Institute of Statistics).

## Problem: API Access Restrictions

The ISTAT SDMX API currently returns 403 Forbidden errors when attempting programmatic access. This appears to be an access restriction or authentication requirement.

## Solutions

We provide **two approaches** to work with ISTAT school data:

---

## Option 1: Automated Download (download_schools_by_region.py)

**Status**: Currently blocked by API restrictions

This Python script attempts to download data directly from ISTAT's SDMX API.

### Usage:
```bash
python3 download_schools_by_region.py
```

### Dataset Information:
- **Dataset ID**: `52_1044_DF_DCIS_SCUOLE_5`
- **Description**: Number of schools by region in Italy
- **Coverage**: 2010 onwards

### Requirements:
```bash
pip install pandasdmx pandas requests
```

### Note:
This script will try multiple methods and formats. If successful, it will save:
- `schools_by_region_raw.csv` - All downloaded data
- `schools_by_region_2010_onwards.csv` - Filtered for 2010+

---

## Option 2: Manual Download + Processing ⭐ RECOMMENDED

**Status**: ✓ Working

Since the API is restricted, you can manually download data from ISTAT and process it with our script.

### Step 1: Download Data from ISTAT Website

Visit the ISTAT website and download school data:

1. **Go to**: https://www.istat.it/
2. **Navigate to**: Statistics → Education → Schools (Scuole)
3. **Or directly**: http://dati.istat.it/
4. **Search for**: "scuole per regione" or dataset ID "DCIS_SCUOLE"
5. **Download** the data as CSV

### Step 2: Process the Downloaded Data

Use the manual processing script:

```bash
# Place your downloaded CSV file in this directory, then run:
python3 process_istat_schools_manual.py

# Or specify the file path:
python3 process_istat_schools_manual.py path/to/downloaded_file.csv
```

### What the script does:
- ✓ Automatically detects column names (year, region, value)
- ✓ Handles different CSV formats and encodings
- ✓ Filters for years >= 2010
- ✓ Generates summary statistics by region
- ✓ Saves processed data

### Output files:
- `processed_[filename].csv` - Cleaned and filtered data
- `schools_by_region_combined.csv` - Combined data if multiple files

---

## Option 3: R Script (download_schools_by_region.R)

**Status**: Should work with R's istat package

The R version uses the `istat` package which may have different access permissions.

### Usage:
```r
# Install required package
install.packages("istat")
install.packages("tidyverse")

# Run the script
source("download_schools_by_region.R")

# Or from command line:
Rscript download_schools_by_region.R
```

### R Code Example:
```r
library(istat)
library(tidyverse)

schools_data <- get_istatdata(
  agencyId = "IT1",
  dataset_id = "52_1044_DF_DCIS_SCUOLE_5",
  version = "1.0",
  start = NULL,
  end = NULL,
  recent = FALSE,
  csv = TRUE,
  xlsx = FALSE
)
```

---

## Troubleshooting

### API returns 403 Forbidden
- This is expected with current ISTAT API restrictions
- Use **Option 2** (manual download) instead

### Cannot find the dataset on ISTAT website
- Try searching for: "istruzione", "scuole", "education"
- Browse by theme: Education and Training
- Alternative datasets may have different IDs

### CSV file won't parse
- The manual processing script tries multiple encodings
- Check if the file is actually CSV (not Excel)
- Try opening in a text editor to check the format

### Different column names
- The script automatically detects common column name variations
- If it fails, check the output and modify the `identify_columns()` function

---

## Data Dictionary

Expected columns in ISTAT school data:

| Column | Italian | Description |
|--------|---------|-------------|
| Year | Anno / TIME_PERIOD | Year of observation |
| Region | Territorio / Regione / ITTER107 | Italian region name or code |
| Value | Valore / OBS_VALUE | Number of schools |
| School Type | Tipo scuola / Ordine | Elementary, Middle, High school, etc. |

---

## Alternative Data Sources

If ISTAT access continues to be problematic:

1. **Eurostat**: European statistics database
   - Website: https://ec.europa.eu/eurostat
   - Has Italian education data

2. **MIUR**: Italian Ministry of Education
   - Website: https://dati.istruzione.it/
   - Open data portal with school statistics

3. **Data.gov.it**: Italian open data portal
   - Website: https://www.dati.gov.it/
   - Search for "scuole"

---

## Contact & Support

For issues with ISTAT API access:
- ISTAT Contact: https://www.istat.it/en/about-us/contact-us
- ISTAT Help Desk: dcmt@istat.it

For script issues:
- Check the script output for error messages
- Try the manual download option
- Verify your Python/R installation

---

## Summary

| Method | Status | Difficulty | Recommended |
|--------|--------|------------|-------------|
| Python API | ❌ Blocked | Easy | No |
| Python Manual | ✅ Works | Easy | **Yes** |
| R istat package | ❓ Unknown | Medium | Try it |
| Manual download | ✅ Works | Very Easy | **Yes** |

**Recommendation**: Use Option 2 (manual download + Python processing) for the most reliable results.
