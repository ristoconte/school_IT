# Regional School Projections for Italy

This repository contains a complete analysis of elementary school projections for Italian regions through 2080, using the ratio method to combine historical school data with population projections.

## 📊 Overview

The analysis combines:
- **Historical school data** (2015-2022) from ISTAT: number of schools and enrollments by region
- **Population projections** (2024-2080) from ISTAT: children aged 6-10 by region
- **Ratio method**: Projects schools based on historical student-to-school ratios

## 🗺️ NUTS Code Mapping Issue (IMPORTANT!)

### The Problem
The `elementari.csv` file uses an **older NUTS classification** that doesn't match current standards:

| elementari.csv | Current NUTS | Region |
|----------------|--------------|--------|
| ITD1, ITD2, ITD3, ITD4, ITD5, ITDA | ITH1, ITH2, ITH3, ITH4, ITH5 | Northeast regions |
| ITE1, ITE2, ITE3, ITE4 | ITI1, ITI2, ITI3, ITI4 | Central regions |

### Our Solution
We created complete mappings for all 22 NUTS2 regions that handle both classifications:

**Regions Covered (22 total):**
- Northwest: Piemonte, Valle d'Aosta, Liguria, Lombardia
- Northeast: Bolzano, Trento, Trentino-Alto Adige, Veneto, Friuli-Venezia Giulia, Emilia-Romagna
- Center: Toscana, Umbria, Marche, Lazio
- South: Abruzzo, Molise, Campania, Puglia, Basilicata, Calabria
- Islands: Sicilia, Sardegna

## 📁 Files

### Data Files
- `elementari.csv` - ISTAT school data (2015-2022): schools and enrollments by region
- `elementary_children_by_region_year.csv` - Population projections (2024-2080)
- `Reg01012022_g/` - Italian regions shapefile for mapping

### Python Scripts
- `regional_school_projections.py` - Main analysis pipeline
- `visualize_regional_projections.py` - Creates charts and plots
- `create_regional_maps.py` - Creates geographic maps using shapefile

### R Scripts
- `regional_school_analysis.R` - Complete analysis (replicates Python)
- `create_regional_maps.R` - Visualizations and maps

### Output Files
- `school_projections_by_region.csv` - Detailed projections for all regions/years
- `regional_school_decline_statistics.csv` - Summary statistics
- `regional_school_summary_table.csv` - Formatted comparison table
- Various PNG/PDF maps and charts

## 🚀 Quick Start

### Python

```bash
# 1. Install dependencies
pip install pandas numpy matplotlib seaborn geopandas

# 2. Run main analysis
python3 regional_school_projections.py

# 3. Create visualizations
python3 visualize_regional_projections.py

# 4. Create maps
python3 create_regional_maps.py
```

### R

```r
# 1. Install dependencies
install.packages(c("tidyverse", "sf", "scales", "RColorBrewer", "viridis"))

# 2. Run main analysis
source("regional_school_analysis.R")

# 3. Create visualizations and maps
source("create_regional_maps.R")
```

## 📈 Methodology

### 1. Data Processing
Following the Stata code logic:
```
- Filter: SEX == "T", CITIZENSHIP == "TOTAL", TYPE_SCHOOL_MANAGEMENT == "ALL"
- Keep only: DATA_TYPE in ["SCHO", "ENR"] (schools and enrollment)
- Reshape wide format
```

### 2. Ratio Method
For each region:
1. Calculate historical student-to-school ratios (post-1990)
2. Compute percentiles: min, median, max
3. Project schools: `Projected Schools = Projected Students / Ratio`
4. Use median as point estimate, min/max as confidence interval

### 3. Key Assumptions
- Children aged 6-10 used as proxy for enrollment
- Historical ratios remain stable (median from post-1990 data)
- No major policy changes affecting school consolidation

## 📊 Key Results

### Top 10 Regions by Projected Change (2050)

| Region | 2022 Schools | 2050 Change | 2080 Change |
|--------|-------------|-------------|-------------|
| Sardegna | 490 | +16% | -16% |
| Basilicata | 191 | +19% | -15% |
| Calabria | 808 | +24% | -9% |
| Puglia | 756 | +25% | -12% |
| Campania | 1,751 | +27% | -9% |
| Sicilia | 1,451 | +32% | -3% |
| Molise | 112 | +41% | +9% |
| Umbria | 289 | +42% | +17% |
| Marche | 444 | +43% | +19% |
| Abruzzo | 401 | +46% | +18% |

### Regions with Strongest Growth
- **Lombardia**: +76% by 2050, +62% by 2080
- **Liguria**: +75% by 2050, +51% by 2080
- **Emilia-Romagna**: +77% by 2050, +59% by 2080
- **Trentino-Alto Adige**: +96% by 2050, +91% by 2080

### Two Distinct Patterns

**Pattern A - Peak and Decline** (Southern regions):
- Initial growth through 2050
- Decline by 2080
- Examples: Sardegna, Basilicata, Calabria, Puglia, Campania, Sicilia

**Pattern B - Sustained Growth** (Northern regions):
- Continued growth through 2080
- Examples: Lombardia, Emilia-Romagna, Veneto, Piemonte, Liguria

## ⚠️ Limitations and Caveats

### 1. Data Limitations
- Only 19 of 20 regions have complete data (Valle d'Aosta naming mismatch)
- Historical data limited to 2015-2022
- Two autonomous provinces (Bolzano, Trento) may have slight inconsistencies

### 2. Methodological Assumptions
- **Enrollment proxy**: Using total children (6-10) instead of actual enrollment
  - May overestimate if enrollment rates decline
  - Doesn't account for private schools vs public schools separately
- **Ratio stability**: Assumes student-teacher ratios remain constant
  - Policy changes (e.g., school consolidation) not modeled
  - Doesn't account for urban/rural differences

### 3. Surprising Results
The projections show **growth** rather than decline for most regions by 2050, which seems counterintuitive given demographic projections. Possible explanations:
- Scale mismatch between total children and enrolled students
- Enrollment rates may differ from 100%
- Need to calculate actual enrollment rates from historical data

## 🔧 Improvements for Future Work

1. **Calculate Enrollment Rates**
   ```python
   enrollment_rate = historical_students / historical_children_6_10
   projected_students = projected_children_6_10 * enrollment_rate
   ```

2. **Add Urban/Rural Breakdown**
   - Different ratios for urban vs rural schools
   - Account for school consolidation trends

3. **Policy Scenarios**
   - Model different school consolidation policies
   - Test sensitivity to ratio assumptions

4. **Validate Against Recent Trends**
   - Compare 2015-2022 trend with pre-2015 data
   - Check if projections align with observed changes

## 📚 Data Sources

- **ISTAT**: Italian National Institute of Statistics
  - School data: Dataset `52_1044_DF_DCIS_SCUOLE_5`
  - Population projections: Regional demographic projections
  - Shapefile: Official ISTAT regional boundaries (2022)

## 🤝 Contributing

This analysis follows the methodology described in the Stata code for national-level projections, adapted for regional analysis.

## 📝 Citation

If using this analysis, please cite:
- Data source: ISTAT (Italian National Institute of Statistics)
- Methodology: Ratio method for school projections
- Code: Available in this repository (Python and R implementations)

## 📞 Contact

For questions about:
- **ISTAT data**: https://www.istat.it/en/about-us/contact-us
- **NUTS classifications**: https://ec.europa.eu/eurostat/web/nuts
- **This analysis**: See repository issues

---

**Generated**: October 2025
**Analysis Period**: 2015-2080
**Geographic Coverage**: 22 Italian NUTS2 regions
