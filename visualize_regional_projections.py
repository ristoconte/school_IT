#!/usr/bin/env python3
"""
Visualize Regional School Projections
Creates plots and maps showing projected school numbers by region
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

def plot_regional_trends(df, top_n=5):
    """
    Plot school projections for top N regions with most schools.
    """
    print("\nCreating regional trends plot...")

    # Get regions with most schools in 2022
    regions_2022 = df[df['year'] == 2022].nlargest(top_n, 'scuole')['region'].tolist()

    fig, axes = plt.subplots(2, 1, figsize=(12, 10))

    # Plot 1: Number of schools
    ax1 = axes[0]
    for region in regions_2022:
        region_data = df[df['region'] == region].sort_values('year')

        # Historical
        hist = region_data[region_data['scuole'].notna()]
        ax1.plot(hist['year'], hist['scuole'], '-o', linewidth=2, markersize=4,
                label=region, alpha=0.8)

        # Projections
        proj = region_data[region_data['proj'] == 'BSL']
        if len(proj) > 0:
            ax1.plot(proj['year'], proj['scuole_hat'], '--', linewidth=1.5, alpha=0.6)

            # Confidence interval
            ax1.fill_between(proj['year'], proj['scuole_lcl'], proj['scuole_ucl'],
                            alpha=0.15)

    ax1.axvline(x=2022, color='red', linestyle=':', alpha=0.5, label='2022 (Last observed)')
    ax1.set_xlabel('Year', fontsize=11)
    ax1.set_ylabel('Number of Schools', fontsize=11)
    ax1.set_title('Elementary School Projections by Region\n(Top 5 Regions by 2022 School Count)',
                 fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9, loc='best')
    ax1.grid(True, alpha=0.3)

    # Plot 2: Indexed (2022 = 100)
    ax2 = axes[1]
    for region in regions_2022:
        region_data = df[df['region'] == region].sort_values('year')

        # Get 2022 baseline
        baseline_2022 = region_data[region_data['year'] == 2022]['scuole'].values
        if len(baseline_2022) == 0:
            continue
        baseline = baseline_2022[0]

        # Historical indexed
        hist = region_data[region_data['scuole'].notna()].copy()
        hist['indexed'] = (hist['scuole'] / baseline) * 100
        ax2.plot(hist['year'], hist['indexed'], '-o', linewidth=2, markersize=4,
                label=region, alpha=0.8)

        # Projections indexed
        proj = region_data[region_data['proj'] == 'BSL'].copy()
        if len(proj) > 0:
            proj['indexed'] = (proj['scuole_hat'] / baseline) * 100
            ax2.plot(proj['year'], proj['indexed'], '--', linewidth=1.5, alpha=0.6)

    ax2.axvline(x=2022, color='red', linestyle=':', alpha=0.5)
    ax2.axhline(y=100, color='gray', linestyle=':', alpha=0.5)
    ax2.set_xlabel('Year', fontsize=11)
    ax2.set_ylabel('Index (2022 = 100)', fontsize=11)
    ax2.set_title('Elementary School Projections - Indexed to 2022',
                 fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9, loc='best')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('regional_school_trends.png', dpi=300, bbox_inches='tight')
    plt.savefig('regional_school_trends.pdf', bbox_inches='tight')
    print("  ✓ Saved: regional_school_trends.png/pdf")
    plt.close()


def plot_decline_map(stats_df):
    """
    Create a heatmap/bar chart showing projected decline by region.
    """
    print("\nCreating regional decline visualization...")

    # Sort by 2050 change
    stats_sorted = stats_df.sort_values('pct_change_2050')

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # Plot 1: Percentage change by 2050
    ax1 = axes[0]
    colors = ['darkred' if x < 0 else 'darkgreen' for x in stats_sorted['pct_change_2050']]
    bars1 = ax1.barh(range(len(stats_sorted)), stats_sorted['pct_change_2050'],
                     color=colors, alpha=0.7)

    ax1.set_yticks(range(len(stats_sorted)))
    ax1.set_yticklabels(stats_sorted['region'], fontsize=10)
    ax1.set_xlabel('Percentage Change (%)', fontsize=11)
    ax1.set_title('Projected Change in Number of Schools by 2050\n(from 2022 baseline)',
                 fontsize=12, fontweight='bold')
    ax1.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    ax1.grid(axis='x', alpha=0.3)

    # Add value labels
    for i, (idx, row) in enumerate(stats_sorted.iterrows()):
        value = row['pct_change_2050']
        ax1.text(value, i, f'  {value:.1f}%', va='center',
                ha='left' if value >= 0 else 'right', fontsize=9)

    # Plot 2: Percentage change by 2080
    ax2 = axes[1]
    stats_sorted_2080 = stats_df.sort_values('pct_change_2080')
    colors = ['darkred' if x < 0 else 'darkgreen' for x in stats_sorted_2080['pct_change_2080']]
    bars2 = ax2.barh(range(len(stats_sorted_2080)), stats_sorted_2080['pct_change_2080'],
                     color=colors, alpha=0.7)

    ax2.set_yticks(range(len(stats_sorted_2080)))
    ax2.set_yticklabels(stats_sorted_2080['region'], fontsize=10)
    ax2.set_xlabel('Percentage Change (%)', fontsize=11)
    ax2.set_title('Projected Change in Number of Schools by 2080\n(from 2022 baseline)',
                 fontsize=12, fontweight='bold')
    ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    ax2.grid(axis='x', alpha=0.3)

    # Add value labels
    for i, (idx, row) in enumerate(stats_sorted_2080.iterrows()):
        value = row['pct_change_2080']
        ax2.text(value, i, f'  {value:.1f}%', va='center',
                ha='left' if value >= 0 else 'right', fontsize=9)

    plt.tight_layout()
    plt.savefig('regional_school_decline_map.png', dpi=300, bbox_inches='tight')
    plt.savefig('regional_school_decline_map.pdf', bbox_inches='tight')
    print("  ✓ Saved: regional_school_decline_map.png/pdf")
    plt.close()


def plot_student_school_ratio(df, top_n=8):
    """Plot student-to-school ratio trends."""
    print("\nCreating student-to-school ratio plot...")

    # Get regions with data
    regions_with_data = df[df['ratio'].notna()]['region'].unique()[:top_n]

    fig, ax = plt.subplots(figsize=(12, 6))

    for region in regions_with_data:
        region_data = df[df['region'] == region].sort_values('year')

        # Historical ratio
        hist = region_data[region_data['ratio'].notna()]
        ax.plot(hist['year'], hist['ratio'], '-o', linewidth=2, markersize=4,
               label=region, alpha=0.8)

    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel('Students per School', fontsize=11)
    ax.set_title('Student-to-School Ratio by Region\n(Historical Data)',
                fontsize=12, fontweight='bold')
    ax.legend(fontsize=9, loc='best', ncol=2)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('student_school_ratio.png', dpi=300, bbox_inches='tight')
    plt.savefig('student_school_ratio.pdf', bbox_inches='tight')
    print("  ✓ Saved: student_school_ratio.png/pdf")
    plt.close()


def create_summary_table(stats_df):
    """Create a formatted summary table."""
    print("\nCreating summary table...")

    # Create a nicely formatted table
    summary = stats_df.copy()
    summary = summary.sort_values('pct_change_2050')

    # Format columns
    summary['Schools 2022'] = summary['schools_2022'].round(0).astype(int)
    summary['Schools 2050'] = summary['schools_2050'].round(0).astype(int)
    summary['Change 2050 (%)'] = summary['pct_change_2050'].round(1)
    summary['Schools 2080'] = summary['schools_2080'].round(0).astype(int)
    summary['Change 2080 (%)'] = summary['pct_change_2080'].round(1)

    # Select and rename columns
    table = summary[['region', 'Schools 2022', 'Schools 2050', 'Change 2050 (%)',
                     'Schools 2080', 'Change 2080 (%)']].copy()
    table.columns = ['Region', '2022', '2050 (Projected)', 'Change 2050 (%)',
                     '2080 (Projected)', 'Change 2080 (%)']

    # Save to CSV
    table.to_csv('regional_school_summary_table.csv', index=False)
    print("  ✓ Saved: regional_school_summary_table.csv")

    # Print to console
    print("\n" + "="*70)
    print("SUMMARY TABLE: Regional School Projections")
    print("="*70)
    print(table.to_string(index=False))
    print("="*70)

    return table


def main():
    """Main visualization function."""
    print("="*70)
    print("Regional School Projections - Visualization")
    print("="*70)

    # Load data
    df = pd.read_csv('school_projections_by_region.csv')
    stats_df = pd.read_csv('regional_school_decline_statistics.csv')

    print(f"\nLoaded {len(df)} projection records for {df['region'].nunique()} regions")

    # Create visualizations
    plot_regional_trends(df, top_n=5)
    plot_decline_map(stats_df)
    plot_student_school_ratio(df, top_n=8)
    summary_table = create_summary_table(stats_df)

    print("\n" + "="*70)
    print("Visualization Complete!")
    print("="*70)
    print("\nGenerated files:")
    print("  - regional_school_trends.png/pdf")
    print("  - regional_school_decline_map.png/pdf")
    print("  - student_school_ratio.png/pdf")
    print("  - regional_school_summary_table.csv")


if __name__ == "__main__":
    main()
