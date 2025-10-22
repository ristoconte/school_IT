#!/usr/bin/env python3
"""
Create geographic maps showing regional school projections using shapefile
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap, Normalize
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Mapping from shapefile COD_REG to region names (must match our data)
COD_REG_TO_REGION = {
    1: 'Piemonte',
    2: "Valle d'Aosta",
    3: 'Lombardia',
    4: 'Trentino-Alto Adige',
    5: 'Veneto',
    6: 'Friuli-Venezia Giulia',
    7: 'Liguria',
    8: 'Emilia-Romagna',
    9: 'Toscana',
    10: 'Umbria',
    11: 'Marche',
    12: 'Lazio',
    13: 'Abruzzo',
    14: 'Molise',
    15: 'Campania',
    16: 'Puglia',
    17: 'Basilicata',
    18: 'Calabria',
    19: 'Sicilia',
    20: 'Sardegna',
}


def load_and_prepare_data():
    """Load shapefile and statistics data."""
    print("="*70)
    print("Loading Data for Mapping")
    print("="*70)

    # Load shapefile
    print("\nLoading shapefile...")
    gdf = gpd.read_file('Reg01012022_g/Reg01012022_g_WGS84.shp')
    print(f"  ✓ Loaded {len(gdf)} regions from shapefile")

    # Load statistics
    print("\nLoading statistics...")
    stats_df = pd.read_csv('regional_school_decline_statistics.csv')
    print(f"  ✓ Loaded statistics for {len(stats_df)} regions")

    # Map COD_REG to region names
    gdf['region'] = gdf['COD_REG'].map(COD_REG_TO_REGION)

    # Merge with statistics
    gdf = gdf.merge(stats_df, on='region', how='left')

    print(f"\n  Regions in shapefile: {len(gdf)}")
    print(f"  Regions with data: {gdf['pct_change_2050'].notna().sum()}")

    if gdf['pct_change_2050'].isna().any():
        print(f"\n  ⚠ Warning: {gdf['pct_change_2050'].isna().sum()} regions missing data:")
        missing = gdf[gdf['pct_change_2050'].isna()]['region'].tolist()
        for m in missing:
            print(f"    - {m}")

    return gdf


def create_diverging_map(gdf, column, year, title, filename):
    """Create a diverging colormap showing increases and decreases."""
    print(f"\nCreating map: {title}...")

    fig, ax = plt.subplots(1, 1, figsize=(12, 14))

    # Create custom diverging colormap (red for decline, green for growth)
    colors = ['#d73027', '#f46d43', '#fdae61', '#fee08b', '#ffffbf',
              '#d9ef8b', '#a6d96a', '#66bd63', '#1a9850']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)

    # Get data range
    vmin = gdf[column].min()
    vmax = gdf[column].max()

    # Center on 0 for diverging colormap
    abs_max = max(abs(vmin), abs(vmax))
    norm = Normalize(vmin=-abs_max, vmax=abs_max)

    # Plot
    gdf.plot(column=column,
             cmap=cmap,
             norm=norm,
             linewidth=0.5,
             edgecolor='black',
             ax=ax,
             legend=False,
             missing_kwds={'color': 'lightgrey', 'label': 'No data'})

    # Add region labels
    for idx, row in gdf.iterrows():
        if pd.notna(row[column]):
            # Get centroid for label placement
            centroid = row.geometry.centroid
            value = row[column]
            label = f"{value:.1f}%"

            # Adjust font size based on region size
            ax.annotate(label, xy=(centroid.x, centroid.y),
                       ha='center', va='center',
                       fontsize=7, weight='bold',
                       color='white' if abs(value) > 20 else 'black',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.3 if abs(value) > 20 else 0))

    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='horizontal',
                       fraction=0.046, pad=0.04)
    cbar.set_label('Percentage Change (%)', fontsize=11, weight='bold')

    # Title and styling
    ax.set_title(title, fontsize=14, weight='bold', pad=20)
    ax.axis('off')

    # Add legend for missing data if any
    if gdf[column].isna().any():
        grey_patch = mpatches.Patch(color='lightgrey', label='No data')
        ax.legend(handles=[grey_patch], loc='lower right')

    plt.tight_layout()
    plt.savefig(f'{filename}.png', dpi=300, bbox_inches='tight')
    plt.savefig(f'{filename}.pdf', bbox_inches='tight')
    print(f"  ✓ Saved: {filename}.png/pdf")
    plt.close()


def create_absolute_map(gdf, column, year, title, filename):
    """Create a map showing absolute number of schools."""
    print(f"\nCreating map: {title}...")

    fig, ax = plt.subplots(1, 1, figsize=(12, 14))

    # Create colormap for absolute values
    cmap = plt.cm.YlOrRd

    # Plot
    gdf.plot(column=column,
             cmap=cmap,
             linewidth=0.5,
             edgecolor='black',
             ax=ax,
             legend=True,
             legend_kwds={'label': 'Number of Schools', 'orientation': 'horizontal',
                         'shrink': 0.8, 'aspect': 30},
             missing_kwds={'color': 'lightgrey', 'label': 'No data'})

    # Add region labels
    for idx, row in gdf.iterrows():
        if pd.notna(row[column]):
            centroid = row.geometry.centroid
            value = row[column]
            label = f"{int(value)}"

            ax.annotate(label, xy=(centroid.x, centroid.y),
                       ha='center', va='center',
                       fontsize=8, weight='bold',
                       color='white',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.5))

    # Title and styling
    ax.set_title(title, fontsize=14, weight='bold', pad=20)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(f'{filename}.png', dpi=300, bbox_inches='tight')
    plt.savefig(f'{filename}.pdf', bbox_inches='tight')
    print(f"  ✓ Saved: {filename}.png/pdf")
    plt.close()


def create_category_map(gdf):
    """Create a categorical map showing growth vs decline patterns."""
    print(f"\nCreating categorical map...")

    # Categorize regions
    def categorize(row):
        if pd.isna(row['pct_change_2050']):
            return 'No data'
        elif row['pct_change_2050'] < -10:
            return 'Strong Decline (< -10%)'
        elif row['pct_change_2050'] < 0:
            return 'Moderate Decline (0 to -10%)'
        elif row['pct_change_2050'] < 20:
            return 'Moderate Growth (0 to 20%)'
        elif row['pct_change_2050'] < 50:
            return 'Strong Growth (20 to 50%)'
        else:
            return 'Very Strong Growth (> 50%)'

    gdf['category'] = gdf.apply(categorize, axis=1)

    fig, ax = plt.subplots(1, 1, figsize=(12, 14))

    # Define colors for categories
    category_colors = {
        'Strong Decline (< -10%)': '#d73027',
        'Moderate Decline (0 to -10%)': '#fc8d59',
        'Moderate Growth (0 to 20%)': '#fee08b',
        'Strong Growth (20 to 50%)': '#a6d96a',
        'Very Strong Growth (> 50%)': '#1a9850',
        'No data': 'lightgrey'
    }

    # Plot
    for category, color in category_colors.items():
        subset = gdf[gdf['category'] == category]
        if len(subset) > 0:
            subset.plot(ax=ax, color=color, edgecolor='black', linewidth=0.5,
                       label=category)

    # Add region labels
    for idx, row in gdf.iterrows():
        if pd.notna(row['pct_change_2050']):
            centroid = row.geometry.centroid
            # Use abbreviated region names for cleaner map
            label = row['DEN_REG'][:8] if len(row['DEN_REG']) > 8 else row['DEN_REG']

            ax.annotate(label, xy=(centroid.x, centroid.y),
                       ha='center', va='center',
                       fontsize=7, weight='bold',
                       color='black')

    # Title and styling
    ax.set_title('Regional School Projections by 2050\nCategorical View',
                fontsize=14, weight='bold', pad=20)
    ax.axis('off')
    ax.legend(loc='lower right', fontsize=9, frameon=True, fancybox=True, shadow=True)

    plt.tight_layout()
    plt.savefig('regional_school_map_categorical.png', dpi=300, bbox_inches='tight')
    plt.savefig('regional_school_map_categorical.pdf', bbox_inches='tight')
    print(f"  ✓ Saved: regional_school_map_categorical.png/pdf")
    plt.close()


def main():
    """Main function to create all maps."""
    print("="*70)
    print("Regional School Projection Maps")
    print("="*70)

    # Load data
    gdf = load_and_prepare_data()

    # Create maps
    create_diverging_map(
        gdf, 'pct_change_2050', 2050,
        'Projected Change in Primary Schools by 2050\n(% change from 2022 baseline)',
        'regional_school_map_2050'
    )

    create_diverging_map(
        gdf, 'pct_change_2080', 2080,
        'Projected Change in Primary Schools by 2080\n(% change from 2022 baseline)',
        'regional_school_map_2080'
    )

    create_absolute_map(
        gdf, 'schools_2022', 2022,
        'Number of Primary Schools in 2022\n(Observed)',
        'regional_school_map_2022_absolute'
    )

    create_absolute_map(
        gdf, 'schools_2050', 2050,
        'Projected Number of Primary Schools in 2050',
        'regional_school_map_2050_absolute'
    )

    create_category_map(gdf)

    print("\n" + "="*70)
    print("Map Creation Complete!")
    print("="*70)
    print("\nGenerated files:")
    print("  - regional_school_map_2050.png/pdf (% change by 2050)")
    print("  - regional_school_map_2080.png/pdf (% change by 2080)")
    print("  - regional_school_map_2022_absolute.png/pdf (2022 schools)")
    print("  - regional_school_map_2050_absolute.png/pdf (2050 projected)")
    print("  - regional_school_map_categorical.png/pdf (categorical view)")


if __name__ == "__main__":
    main()
