#!/usr/bin/env python3
"""
Regional School Projections for Italy
Combines historical school data with population projections to forecast
the number of schools by region using the ratio method.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# NUTS code to region name mapping
NUTS_TO_REGION = {
    'ITC1': 'Piemonte',
    'ITC2': 'Valle d Aosta-Vallee d Aoste',
    'ITC3': 'Liguria',
    'ITC4': 'Lombardia',
    'ITH1': 'Provincia autonoma di Bolzano',
    'ITH2': 'Provincia autonoma di Trento',
    'ITH3': 'Veneto',
    'ITH4': 'Friuli-Venezia Giulia',
    'ITH5': 'Emilia-Romagna',
    'ITI1': 'Toscana',
    'ITI2': 'Umbria',
    'ITI3': 'Marche',
    'ITI4': 'Lazio',
    'ITF1': 'Abruzzo',
    'ITF2': 'Molise',
    'ITF3': 'Campania',
    'ITF4': 'Puglia',
    'ITF5': 'Basilicata',
    'ITF6': 'Calabria',
    'ITG1': 'Sicilia',
    'ITG2': 'Sardegna',
    # Trentino-Alto Adige is aggregated
    'ITH': 'Trentino-Alto Adige'
}

def process_school_data(filepath='elementari.csv'):
    """
    Process the elementari.csv file following the Stata code logic:
    - Keep only: sex=="T", citizenship=="TOTAL", type_school_management=="ALL"
    - Keep only data_type in ["SCHO", "ENR"]
    - Reshape wide
    """
    print("="*70)
    print("Processing School Data")
    print("="*70)

    # Read the CSV
    df = pd.read_csv(filepath)

    print(f"\nOriginal data: {len(df)} rows")
    print(f"Columns: {df.columns.tolist()}\n")

    # Filter according to Stata code
    df_filtered = df[
        (df['SEX'] == 'T') &
        (df['CITIZENSHIP'] == 'TOTAL') &
        (df['TYPE_SCHOOL_MANAGEMENT'] == 'ALL') &
        (df['DATA_TYPE'].isin(['SCHO', 'ENR']))
    ].copy()

    print(f"After filtering: {len(df_filtered)} rows")

    # Keep only needed columns
    df_filtered = df_filtered[['REF_AREA', 'DATA_TYPE', 'obsTime', 'obsValue']]

    # Rename columns to match Stata naming
    df_filtered = df_filtered.rename(columns={
        'obsTime': 'year',
        'obsValue': 'value',
        'REF_AREA': 'ref_area'
    })

    # Reshape wide (pivot data_type to columns)
    df_wide = df_filtered.pivot_table(
        index=['ref_area', 'year'],
        columns='DATA_TYPE',
        values='value',
        aggfunc='sum'
    ).reset_index()

    # Rename columns
    df_wide.columns.name = None
    df_wide = df_wide.rename(columns={
        'ENR': 'studenti',
        'SCHO': 'scuole'
    })

    # Convert year to numeric
    df_wide['year'] = pd.to_numeric(df_wide['year'])

    # Map NUTS codes to region names
    df_wide['region'] = df_wide['ref_area'].map(NUTS_TO_REGION)

    # Filter for main regions (NUTS2 level - 3 or 4 character codes starting with IT)
    # Exclude national total (IT) and sub-regional levels
    df_wide = df_wide[df_wide['ref_area'].str.len().isin([4])]
    df_wide = df_wide[df_wide['region'].notna()]

    print(f"\nFinal dataset: {len(df_wide)} rows")
    print(f"Years: {df_wide['year'].min()} - {df_wide['year'].max()}")
    print(f"Regions: {df_wide['region'].nunique()}")
    print(f"\nRegions covered:")
    for region in sorted(df_wide['region'].unique()):
        print(f"  - {region}")

    return df_wide


def load_population_projections(filepath='elementary_children_by_region_year.csv'):
    """Load population projections for children aged 6-10."""
    print("\n" + "="*70)
    print("Loading Population Projections")
    print("="*70)

    df = pd.read_csv(filepath)

    # Rename columns for consistency
    df = df.rename(columns={
        'Region': 'region',
        'Year': 'year',
        'Children_6_10': 'children_6_10'
    })

    df['year'] = pd.to_numeric(df['year'])

    print(f"\nPopulation projections: {len(df)} rows")
    print(f"Years: {df['year'].min()} - {df['year'].max()}")
    print(f"Regions: {df['region'].nunique()}")

    return df


def merge_data(school_df, pop_df):
    """Merge school data with population projections."""
    print("\n" + "="*70)
    print("Merging Datasets")
    print("="*70)

    # Merge on region and year
    merged = pd.merge(
        school_df,
        pop_df,
        on=['region', 'year'],
        how='outer',
        indicator=True
    )

    # Add a projection indicator
    merged['proj'] = ''
    merged.loc[merged['_merge'] == 'right_only', 'proj'] = 'BSL'  # Baseline projection
    merged.loc[merged['_merge'] == 'both', 'proj'] = ''  # Historical data

    # For historical years, mark as observed
    merged.loc[merged['scuole'].notna() & (merged['year'] < 2023), 'proj'] = ''
    merged.loc[merged['scuole'].isna() & (merged['year'] >= 2023), 'proj'] = 'BSL'

    print(f"\nMerged data: {len(merged)} rows")
    print(f"Historical records (with school data): {len(merged[merged['scuole'].notna()])}")
    print(f"Projection records (population only): {len(merged[merged['proj'] == 'BSL'])}")

    return merged


def calculate_ratio_projections(df):
    """
    Calculate school projections using the ratio method.
    Based on the Stata code logic.
    """
    print("\n" + "="*70)
    print("Calculating School Projections (Ratio Method)")
    print("="*70)

    results = []

    for region in sorted(df['region'].unique()):
        print(f"\nProcessing: {region}")

        region_df = df[df['region'] == region].copy().sort_values('year')

        # Calculate student-to-school ratio for historical data (post-1990)
        historical = region_df[(region_df['scuole'].notna()) & (region_df['year'] > 1990)]

        if len(historical) == 0:
            print(f"  ⚠ No historical data available")
            continue

        # For projection years, use children_6_10 as proxy for studenti
        # Assume enrollment rate of ~100% (can be refined)
        region_df['studenti_proj'] = region_df['studenti'].fillna(region_df['children_6_10'])

        region_df['ratio'] = region_df['studenti'] / region_df['scuole']

        # Calculate percentiles for ratio (min, median, max)
        ratio_values = region_df[region_df['ratio'].notna()]['ratio']

        if len(ratio_values) == 0:
            continue

        ratio_min = ratio_values.min()
        ratio_med = ratio_values.median()
        ratio_max = ratio_values.max()

        print(f"  Ratio - Min: {ratio_min:.1f}, Median: {ratio_med:.1f}, Max: {ratio_max:.1f}")

        # Project schools using the ratio
        region_df['ratio_hat'] = ratio_med
        region_df['ratio_lcl'] = ratio_min
        region_df['ratio_ucl'] = ratio_max

        # For historical data, use observed values
        region_df.loc[region_df['scuole'].notna(), 'ratio_hat'] = region_df['ratio']
        region_df.loc[region_df['scuole'].notna(), 'ratio_lcl'] = region_df['ratio']
        region_df.loc[region_df['scuole'].notna(), 'ratio_ucl'] = region_df['ratio']

        # Calculate projected schools using studenti_proj
        region_df['scuole_hat'] = region_df['studenti_proj'] / region_df['ratio_hat']
        region_df['scuole_lcl'] = region_df['studenti_proj'] / region_df['ratio_ucl']  # Note: inverted
        region_df['scuole_ucl'] = region_df['studenti_proj'] / region_df['ratio_lcl']  # Note: inverted

        # For historical data, preserve actual values
        region_df.loc[region_df['scuole'].notna(), 'scuole_hat'] = region_df['scuole']
        region_df.loc[region_df['scuole'].notna(), 'scuole_lcl'] = region_df['scuole']
        region_df.loc[region_df['scuole'].notna(), 'scuole_ucl'] = region_df['scuole']

        results.append(region_df)

    # Combine all regions
    final_df = pd.concat(results, ignore_index=True)

    print(f"\n✓ Projections calculated for {final_df['region'].nunique()} regions")

    return final_df


def calculate_decline_statistics(df):
    """Calculate decline statistics for each region."""
    print("\n" + "="*70)
    print("Calculating Decline Statistics")
    print("="*70)

    stats = []

    for region in sorted(df['region'].unique()):
        region_df = df[df['region'] == region].sort_values('year')

        # Get 2022 baseline (latest historical)
        baseline_2022 = region_df[region_df['year'] == 2022]['scuole_hat'].values

        # Get 2050 projection
        proj_2050 = region_df[region_df['year'] == 2050]['scuole_hat'].values

        # Get 2080 projection
        proj_2080 = region_df[region_df['year'] == 2080]['scuole_hat'].values

        if len(baseline_2022) > 0 and len(proj_2050) > 0 and len(proj_2080) > 0:
            baseline = baseline_2022[0]

            # Calculate absolute and percentage change
            change_2050 = proj_2050[0] - baseline
            pct_change_2050 = (change_2050 / baseline) * 100

            change_2080 = proj_2080[0] - baseline
            pct_change_2080 = (change_2080 / baseline) * 100

            stats.append({
                'region': region,
                'schools_2022': baseline,
                'schools_2050': proj_2050[0],
                'schools_2080': proj_2080[0],
                'change_2050': change_2050,
                'pct_change_2050': pct_change_2050,
                'change_2080': change_2080,
                'pct_change_2080': pct_change_2080
            })

    stats_df = pd.DataFrame(stats)
    stats_df = stats_df.sort_values('pct_change_2050')

    print("\nTop 10 regions with largest decline by 2050:")
    print(stats_df.head(10)[['region', 'pct_change_2050']].to_string(index=False))

    return stats_df


def save_results(df, stats_df):
    """Save processed data and statistics."""
    print("\n" + "="*70)
    print("Saving Results")
    print("="*70)

    # Save full projections
    output_file = 'school_projections_by_region.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✓ Saved projections to: {output_file}")

    # Save statistics
    stats_file = 'regional_school_decline_statistics.csv'
    stats_df.to_csv(stats_file, index=False)
    print(f"✓ Saved statistics to: {stats_file}")

    return output_file, stats_file


def main():
    """Main execution function."""

    # Step 1: Process school data
    school_df = process_school_data('elementari.csv')

    # Step 2: Load population projections
    pop_df = load_population_projections('elementary_children_by_region_year.csv')

    # Step 3: Merge datasets
    merged_df = merge_data(school_df, pop_df)

    # Step 4: Calculate projections
    final_df = calculate_ratio_projections(merged_df)

    # Step 5: Calculate decline statistics
    stats_df = calculate_decline_statistics(final_df)

    # Step 6: Save results
    save_results(final_df, stats_df)

    print("\n" + "="*70)
    print("Processing Complete!")
    print("="*70)

    return final_df, stats_df


if __name__ == "__main__":
    final_df, stats_df = main()
