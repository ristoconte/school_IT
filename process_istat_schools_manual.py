#!/usr/bin/env python3
"""
Process manually downloaded ISTAT school data
This script works with CSV files downloaded from the ISTAT website
"""

import pandas as pd
import glob
import os

def process_istat_school_file(filepath):
    """Process a CSV file downloaded from ISTAT."""
    print(f"\nProcessing: {os.path.basename(filepath)}")

    # Try different encodings and separators
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1', 'cp1252']
    separators = [',', ';', '\t']

    df = None
    for encoding in encodings:
        for sep in separators:
            try:
                df = pd.read_csv(filepath, encoding=encoding, sep=sep, low_memory=False)
                if df.shape[1] > 1:  # Successfully parsed with multiple columns
                    print(f"  ✓ Loaded with encoding={encoding}, separator='{sep}'")
                    print(f"  Rows: {len(df)}, Columns: {len(df.columns)}")
                    return df
            except Exception:
                continue

    if df is None:
        print(f"  ✗ Could not parse file")
        return None

    return df


def identify_columns(df):
    """Identify year, region, and value columns."""
    columns_info = {
        'year': None,
        'region': None,
        'value': None,
        'school_type': None
    }

    # Possible column names for year
    year_patterns = ['time', 'anno', 'year', 'periodo', 'period', 'data']
    for col in df.columns:
        col_lower = str(col).lower()
        if any(pattern in col_lower for pattern in year_patterns):
            columns_info['year'] = col
            break

    # Possible column names for region
    region_patterns = ['region', 'regione', 'territorio', 'territory', 'itter']
    for col in df.columns:
        col_lower = str(col).lower()
        if any(pattern in col_lower for pattern in region_patterns):
            columns_info['region'] = col
            break

    # Possible column names for value
    value_patterns = ['value', 'valore', 'numero', 'number', 'count', 'obs']
    for col in df.columns:
        col_lower = str(col).lower()
        if any(pattern in col_lower for pattern in value_patterns):
            columns_info['value'] = col
            break

    # School type
    school_patterns = ['tipo', 'type', 'scuola', 'school', 'ordine', 'grado']
    for col in df.columns:
        col_lower = str(col).lower()
        if any(pattern in col_lower for pattern in school_patterns):
            columns_info['school_type'] = col
            break

    return columns_info


def filter_and_process(df, year_col, region_col, value_col, start_year=2010):
    """Filter and process the data for years >= start_year."""

    # Convert year to numeric
    df['year_numeric'] = pd.to_numeric(df[year_col], errors='coerce')

    # Filter for years >= start_year
    df_filtered = df[df['year_numeric'] >= start_year].copy()

    print(f"\n  ✓ Filtered for years >= {start_year}: {len(df_filtered)} rows")
    if len(df_filtered) > 0:
        print(f"  Year range: {int(df_filtered['year_numeric'].min())} - {int(df_filtered['year_numeric'].max())}")

    return df_filtered


def main():
    print("="*70)
    print("Process Manually Downloaded ISTAT School Data")
    print("="*70)
    print()
    print("Instructions:")
    print("1. Download school data from ISTAT website:")
    print("   https://www.istat.it/")
    print("   Navigate to: Statistics > Education > Schools")
    print()
    print("2. Save the CSV file(s) in this directory")
    print()
    print("3. Run this script")
    print()
    print("="*70)
    print()

    # Look for CSV files in current directory (excluding our output files)
    csv_files = glob.glob('*.csv')
    exclude_patterns = ['elementary_children', 'schools_by_region', 'raw', '2010_onwards']
    csv_files = [f for f in csv_files if not any(pattern in f for pattern in exclude_patterns)]

    if not csv_files:
        print("No CSV files found in current directory.")
        print("\nPlease download ISTAT school data and save it as a CSV file here.")
        print("\nAlternatively, specify the file path:")
        print("  python process_istat_schools_manual.py path/to/your/file.csv")
        return

    print(f"Found {len(csv_files)} CSV file(s):")
    for f in csv_files:
        print(f"  - {f}")

    all_data = []

    for csv_file in csv_files:
        df = process_istat_school_file(csv_file)

        if df is None:
            continue

        # Display columns
        print(f"\n  Columns: {df.columns.tolist()}")

        # Try to identify key columns
        cols = identify_columns(df)

        print(f"\n  Identified columns:")
        print(f"    Year: {cols['year']}")
        print(f"    Region: {cols['region']}")
        print(f"    Value: {cols['value']}")
        print(f"    School Type: {cols['school_type']}")

        # Display first few rows
        print(f"\n  First few rows:")
        print(df.head(5).to_string())

        # If key columns identified, filter and process
        if cols['year'] and cols['region'] and cols['value']:
            df_filtered = filter_and_process(df, cols['year'], cols['region'], cols['value'])
            all_data.append(df_filtered)

            # Save individual processed file
            output_name = f"processed_{os.path.basename(csv_file)}"
            df_filtered.to_csv(output_name, index=False)
            print(f"\n  ✓ Saved processed data to: {output_name}")

            # Display summary by region
            print(f"\n  Summary by region (most recent year):")
            most_recent = df_filtered['year_numeric'].max()
            summary = df_filtered[df_filtered['year_numeric'] == most_recent].groupby(cols['region'])[cols['value']].sum().sort_values(ascending=False)
            print(summary.head(10).to_string())

    if all_data:
        # Combine all data
        combined = pd.concat(all_data, ignore_index=True)
        combined.to_csv('schools_by_region_combined.csv', index=False)
        print(f"\n✓ Combined data saved to: schools_by_region_combined.csv")
        print(f"  Total rows: {len(combined)}")

    print("\n" + "="*70)
    print("Processing complete!")
    print("="*70)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # Process specific file
        filepath = sys.argv[1]
        if os.path.exists(filepath):
            df = process_istat_school_file(filepath)
            if df is not None:
                cols = identify_columns(df)
                print(f"\nIdentified columns: {cols}")
                if cols['year'] and cols['value']:
                    df_filtered = filter_and_process(df, cols['year'], cols.get('region', df.columns[0]), cols['value'])
                    output = 'processed_istat_schools.csv'
                    df_filtered.to_csv(output, index=False)
                    print(f"\n✓ Saved to: {output}")
        else:
            print(f"File not found: {filepath}")
    else:
        main()
