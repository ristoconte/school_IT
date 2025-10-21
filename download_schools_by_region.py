#!/usr/bin/env python3
"""
Download number of schools by region in Italy from 2010 onwards
Data source: ISTAT (Italian National Institute of Statistics)
"""

import pandas as pd
import sys

def list_available_dataflows():
    """List available dataflows to help identify the correct dataset."""
    try:
        import pandasdmx as sdmx

        print("Attempting to list available ISTAT dataflows...")
        istat = sdmx.Request('ISTAT')

        # Get available dataflows
        flows = istat.dataflow()

        print("\nSearching for school-related datasets...")
        school_flows = []
        for key, flow in flows.dataflow.items():
            name = str(flow.name).lower()
            if 'scuol' in name or 'school' in name or 'educ' in name:
                school_flows.append((key, flow.name))

        if school_flows:
            print(f"\nFound {len(school_flows)} school-related datasets:")
            for key, name in school_flows:
                print(f"  - {key}: {name}")

        return school_flows
    except Exception as e:
        print(f"Could not list dataflows: {e}")
        return []


def download_with_pandasdmx():
    """Download data using pandasdmx library (SDMX format)."""
    try:
        import pandasdmx as sdmx
    except ImportError:
        print("pandasdmx not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandasdmx"])
        import pandasdmx as sdmx

    print("="*70)
    print("Downloading Schools by Region Data from ISTAT")
    print("="*70)
    print()
    print("Dataset: Number of schools by region in Italy")
    print("Source: ISTAT")
    print("Period: 2010 onwards")
    print()

    # First, try to list available dataflows
    list_available_dataflows()

    # Try different dataset ID formats
    dataset_ids = [
        '52_1044_DF_DCIS_SCUOLE_5',
        'DCIS_SCUOLE_5',
        '52_1044',
        'DF_DCIS_SCUOLE_5'
    ]

    for dataflow_id in dataset_ids:
        try:
            # Create ISTAT data source connection
            print(f"\nAttempting to download with ID: {dataflow_id}")
            istat = sdmx.Request('ISTAT')

            # Request data with different parameter combinations
            print("  Trying without format parameter...")
            data_response = istat.data(
                resource_id=dataflow_id,
                key='all'
            )

            # Convert to pandas DataFrame
            print("  Converting to DataFrame...")
            df = sdmx.to_pandas(data_response)

            # If the result is a Series, convert to DataFrame
            if isinstance(df, pd.Series):
                df = df.reset_index()
                df.columns = list(df.columns[:-1]) + ['Value']

            print(f"✓ Data downloaded successfully!")
            print(f"  Total rows: {len(df)}")
            print(f"  Total columns: {len(df.columns)}")

            return df

        except Exception as e:
            print(f"  ✗ Failed: {str(e)[:100]}")
            continue

    print("\n✗ All pandasdmx attempts failed")
    return None


def download_with_requests():
    """Download data using direct HTTP requests to ISTAT API."""
    import requests
    import json

    print("Using direct API request method...")

    # ISTAT SDMX REST API endpoint
    base_url = "https://sdmx.istat.it/SDMXWS/rest/data"
    dataflow_id = "52_1044_DF_DCIS_SCUOLE_5"

    # Construct URL
    url = f"{base_url}/IT1,{dataflow_id},1.0/all"
    params = {
        'format': 'jsondata',
        'locale': 'it'
    }

    print(f"Requesting: {url}")

    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()

        print("✓ API request successful!")

        # Parse JSON response
        data = response.json()

        # Extract data from SDMX-JSON format
        print("Parsing SDMX-JSON data...")

        # This is a simplified parser - SDMX-JSON structure can be complex
        if 'data' in data:
            observations = []

            # Try to parse the structure
            structure = data.get('structure', {})
            dimensions = structure.get('dimensions', {}).get('observation', [])
            dim_names = [d.get('id', f'dim_{i}') for i, d in enumerate(dimensions)]

            # Get observations
            datasets = data.get('data', {}).get('dataSets', [])
            if datasets:
                obs = datasets[0].get('observations', {})

                for key, values in obs.items():
                    # Parse observation key
                    indices = [int(x) for x in key.split(':')]

                    row = {}
                    for i, dim in enumerate(dimensions):
                        if i < len(indices):
                            dim_id = dim.get('id', f'dim_{i}')
                            dim_values = dim.get('values', [])
                            if indices[i] < len(dim_values):
                                row[dim_id] = dim_values[indices[i]].get('name', str(indices[i]))

                    # Add value
                    row['Value'] = values[0] if isinstance(values, list) else values

                    observations.append(row)

                df = pd.DataFrame(observations)
                print(f"✓ Parsed {len(df)} observations")
                return df

        print("⚠ Could not parse SDMX-JSON structure")
        return None

    except requests.exceptions.RequestException as e:
        print(f"✗ HTTP request failed: {e}")
        return None
    except Exception as e:
        print(f"✗ Error parsing response: {e}")
        return None


def download_with_csv_direct():
    """Try to download CSV directly from ISTAT if available."""
    import requests

    print("Attempting direct CSV download...")

    # ISTAT sometimes provides direct CSV exports
    base_url = "https://sdmx.istat.it/SDMXWS/rest/data"
    dataflow_id = "52_1044_DF_DCIS_SCUOLE_5"

    url = f"{base_url}/IT1,{dataflow_id},1.0/all"
    params = {'format': 'csv'}

    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()

        # Try to read as CSV
        from io import StringIO
        df = pd.read_csv(StringIO(response.text))

        print(f"✓ CSV downloaded successfully!")
        print(f"  Total rows: {len(df)}")
        return df

    except Exception as e:
        print(f"✗ CSV download failed: {e}")
        return None


def process_and_save_data(df):
    """Process and save the downloaded data."""
    if df is None or len(df) == 0:
        print("\n✗ No data to process")
        return

    print("\n" + "="*70)
    print("Processing Data")
    print("="*70)

    # Display column names
    print("\nColumn names:")
    print(df.columns.tolist())

    # Display first few rows
    print("\nFirst few rows:")
    print(df.head(10))

    # Save raw data
    output_raw = "schools_by_region_raw.csv"
    df.to_csv(output_raw, index=False)
    print(f"\n✓ Raw data saved to: {output_raw}")

    # Try to identify and filter by year
    year_columns = ['TIME_PERIOD', 'Anno', 'ANNO', 'Year', 'YEAR', 'time_period', 'anno', 'TIME', 'Time']
    year_col = None

    for col in year_columns:
        if col in df.columns:
            year_col = col
            break

    if year_col:
        print(f"\n✓ Year column identified: '{year_col}'")

        # Convert to numeric and filter
        df['year_numeric'] = pd.to_numeric(df[year_col], errors='coerce')
        df_filtered = df[df['year_numeric'] >= 2010].copy()

        print(f"✓ Filtered for years >= 2010: {len(df_filtered)} rows")
        if len(df_filtered) > 0:
            print(f"  Year range: {int(df_filtered['year_numeric'].min())} - {int(df_filtered['year_numeric'].max())}")

            output_filtered = "schools_by_region_2010_onwards.csv"
            df_filtered.to_csv(output_filtered, index=False)
            print(f"✓ Filtered data saved to: {output_filtered}")

            # Display summary
            display_summary(df_filtered, year_col)
        else:
            print("⚠ No data found for years >= 2010")
    else:
        print("\n⚠ Could not identify year column")
        print("  Available columns:", df.columns.tolist())

    print("\n" + "="*70)
    print("Download and processing complete!")
    print("="*70)


def display_summary(df, year_col):
    """Display summary statistics by region."""

    # Try to find region and value columns
    region_columns = ['ITTER107', 'Territorio', 'TERRITORIO', 'Region', 'REGION',
                     'Regione', 'REGIONE', 'territorio', 'regione', 'REF_AREA']
    value_columns = ['Value', 'VALUE', 'OBS_VALUE', 'Valore', 'VALORE', 'value', 'valore']

    region_col = None
    value_col = None

    for col in region_columns:
        if col in df.columns:
            region_col = col
            break

    for col in value_columns:
        if col in df.columns:
            value_col = col
            break

    if region_col and value_col and year_col:
        print(f"\n✓ Region column: '{region_col}'")
        print(f"✓ Value column: '{value_col}'")

        # Get most recent year
        most_recent = df[year_col].max()

        print(f"\nSummary by region (most recent year: {most_recent}):")

        summary = df[df[year_col] == most_recent].groupby(region_col)[value_col].sum().sort_values(ascending=False)
        print(summary.to_string())


def main():
    """Main function to download and process ISTAT data."""

    # Try different methods in order
    df = None

    # Method 1: pandasdmx (most robust)
    print("Method 1: Using pandasdmx library\n")
    df = download_with_pandasdmx()

    # Method 2: Direct API with requests
    if df is None:
        print("\n\nMethod 2: Using direct API requests\n")
        df = download_with_requests()

    # Method 3: CSV direct download
    if df is None:
        print("\n\nMethod 3: Direct CSV download\n")
        df = download_with_csv_direct()

    # Process the data
    if df is not None:
        process_and_save_data(df)
    else:
        print("\n" + "="*70)
        print("✗ All download methods failed")
        print("="*70)
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify the dataset ID: 52_1044_DF_DCIS_SCUOLE_5")
        print("3. Check if ISTAT API is accessible: https://sdmx.istat.it")
        print("4. Install required packages:")
        print("   pip install pandasdmx requests pandas")
        print("\nAlternatively, visit ISTAT website directly:")
        print("https://www.istat.it/")


if __name__ == "__main__":
    main()
