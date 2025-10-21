#!/usr/bin/env python3
"""
Count elementary school age children (6-10 years) per Italian region per year.
"""

import pandas as pd
import glob
import os
import re

def extract_region_name(filename):
    """Extract region name from filename."""
    # Pattern: it-Popolazione_per_eta_-_Regione_<RegionName>.csv
    match = re.search(r'Regione_(.+)\.csv$', filename)
    if match:
        region = match.group(1).replace('_', ' ')
        return region
    return None

def process_regional_file(filepath):
    """Process a single regional CSV file and extract children aged 6-10."""
    region_name = extract_region_name(os.path.basename(filepath))

    if not region_name:
        print(f"Could not extract region name from {filepath}")
        return None

    # Read CSV, skipping first 2 metadata rows, using utf-8-sig to handle BOM
    # index_col=False prevents pandas from using the first column as index
    df = pd.read_csv(filepath, sep=';', skiprows=2, encoding='utf-8-sig',
                     index_col=False, quotechar='"')

    # Clean column names (remove any extra whitespace and quotes)
    df.columns = df.columns.str.strip().str.strip('"')

    # Filter for ages 6-10 (elementary school age)
    # The age column might be 'Età' or 'Etá' depending on encoding
    age_col = 'Età' if 'Età' in df.columns else 'Etá'

    # Convert age and year to numeric, and clean the median column
    df[age_col] = pd.to_numeric(df[age_col], errors='coerce')
    df['Anno'] = pd.to_numeric(df['Anno'], errors='coerce')
    df['Scenario mediano'] = pd.to_numeric(df['Scenario mediano'], errors='coerce')

    # Filter for ages 6-10 (elementary school age)
    elementary_ages = df[df[age_col].isin([6, 7, 8, 9, 10])].copy()

    # Group by year and sum the median scenario values
    result = elementary_ages.groupby('Anno')['Scenario mediano'].sum().reset_index()
    result.columns = ['Year', 'Children_6_10']
    result['Region'] = region_name

    return result[['Region', 'Year', 'Children_6_10']]

def main():
    """Main function to process all regional files."""
    print("Processing Italian regional population data...")
    print("Counting elementary school age children (ages 6-10) per region per year\n")

    # Find all regional CSV files
    csv_files = glob.glob('it-Popolazione_per_eta_-_Regione_*.csv')

    if not csv_files:
        print("Error: No regional CSV files found!")
        return

    print(f"Found {len(csv_files)} regional files to process\n")

    # Process all files
    all_results = []
    for csv_file in sorted(csv_files):
        print(f"Processing: {csv_file}")
        result = process_regional_file(csv_file)
        if result is not None:
            all_results.append(result)

    # Combine all results
    if all_results:
        combined_df = pd.concat(all_results, ignore_index=True)

        # Sort by region and year
        combined_df = combined_df.sort_values(['Region', 'Year']).reset_index(drop=True)

        # Save to CSV
        output_file = 'elementary_children_by_region_year.csv'
        combined_df.to_csv(output_file, index=False, encoding='utf-8')

        print(f"\n✓ Successfully created: {output_file}")
        print(f"✓ Total records: {len(combined_df)}")
        print(f"✓ Regions covered: {combined_df['Region'].nunique()}")
        print(f"✓ Years covered: {combined_df['Year'].min()} - {combined_df['Year'].max()}")

        # Display sample of results
        print("\nSample of results:")
        print(combined_df.head(10).to_string(index=False))

        # Display summary statistics
        print("\n\nSummary by region (2024):")
        summary_2024 = combined_df[combined_df['Year'] == 2024].sort_values('Children_6_10', ascending=False)
        print(summary_2024.to_string(index=False))

    else:
        print("Error: No data was processed successfully!")

if __name__ == "__main__":
    main()
