#!/usr/bin/env Rscript
#
# Regional School Projections for Italy - Complete Analysis in R
# Replicates the Python analysis with ratio method
#

# Load required libraries
suppressPackageStartupMessages({
  library(tidyverse)
  library(sf)          # For shapefiles
  library(scales)      # For formatting
})

# ==============================================================================
# PART 1: NUTS CODE MAPPINGS
# ==============================================================================

# NUTS code to region name mapping
# Note: elementari.csv uses older NUTS classification (ITD*, ITE* instead of ITH*, ITI*)
NUTS_TO_REGION <- c(
  # ITC - Northwest
  'ITC1' = 'Piemonte',
  'ITC2' = "Valle d'Aosta",
  'ITC3' = 'Liguria',
  'ITC4' = 'Lombardia',
  # ITD - Northeast (old classification)
  'ITD1' = 'Provincia autonoma Bolzano/Bozen',
  'ITD2' = 'Provincia autonoma Trento',
  'ITD3' = 'Veneto',
  'ITD4' = 'Friuli-Venezia Giulia',
  'ITD5' = 'Emilia-Romagna',
  'ITDA' = 'Trentino-Alto Adige',
  # ITE - Center (old classification)
  'ITE1' = 'Toscana',
  'ITE2' = 'Umbria',
  'ITE3' = 'Marche',
  'ITE4' = 'Lazio',
  # ITF - South
  'ITF1' = 'Abruzzo',
  'ITF2' = 'Molise',
  'ITF3' = 'Campania',
  'ITF4' = 'Puglia',
  'ITF5' = 'Basilicata',
  'ITF6' = 'Calabria',
  # ITG - Islands
  'ITG1' = 'Sicilia',
  'ITG2' = 'Sardegna'
)

# Shapefile COD_REG to region names
COD_REG_TO_REGION <- c(
  '1' = 'Piemonte',
  '2' = "Valle d'Aosta",
  '3' = 'Lombardia',
  '4' = 'Trentino-Alto Adige',
  '5' = 'Veneto',
  '6' = 'Friuli-Venezia Giulia',
  '7' = 'Liguria',
  '8' = 'Emilia-Romagna',
  '9' = 'Toscana',
  '10' = 'Umbria',
  '11' = 'Marche',
  '12' = 'Lazio',
  '13' = 'Abruzzo',
  '14' = 'Molise',
  '15' = 'Campania',
  '16' = 'Puglia',
  '17' = 'Basilicata',
  '18' = 'Calabria',
  '19' = 'Sicilia',
  '20' = 'Sardegna'
)

# ==============================================================================
# PART 2: PROCESS SCHOOL DATA
# ==============================================================================

process_school_data <- function(filepath = 'elementari.csv') {
  cat(rep("=", 70), "\n", sep = "")
  cat("Processing School Data\n")
  cat(rep("=", 70), "\n\n", sep = "")

  # Read CSV
  df <- read_csv(filepath, show_col_types = FALSE)
  cat(sprintf("Original data: %d rows\n", nrow(df)))
  cat(sprintf("Columns: %s\n\n", paste(names(df), collapse = ", ")))

  # Filter according to logic:
  # - SEX == "T"
  # - CITIZENSHIP == "TOTAL"
  # - TYPE_SCHOOL_MANAGEMENT == "ALL"
  # - DATA_TYPE in c("SCHO", "ENR")
  df_filtered <- df %>%
    filter(
      SEX == "T",
      CITIZENSHIP == "TOTAL",
      TYPE_SCHOOL_MANAGEMENT == "ALL",
      DATA_TYPE %in% c("SCHO", "ENR")
    )

  cat(sprintf("After filtering: %d rows\n\n", nrow(df_filtered)))

  # Reshape wide (pivot data_type to columns)
  df_wide <- df_filtered %>%
    select(REF_AREA, DATA_TYPE, obsTime, obsValue) %>%
    pivot_wider(
      names_from = DATA_TYPE,
      values_from = obsValue,
      values_fn = sum
    ) %>%
    rename(
      ref_area = REF_AREA,
      year = obsTime,
      studenti = ENR,
      scuole = SCHO
    )

  # Convert year to numeric
  df_wide$year <- as.numeric(df_wide$year)

  # Map NUTS codes to region names
  df_wide$region <- NUTS_TO_REGION[df_wide$ref_area]

  # Filter for main regions (NUTS2 level)
  df_wide <- df_wide %>% filter(!is.na(region))

  cat(sprintf("Final dataset: %d rows\n", nrow(df_wide)))
  cat(sprintf("Years: %d - %d\n", min(df_wide$year), max(df_wide$year)))
  cat(sprintf("Regions: %d\n\n", n_distinct(df_wide$region)))

  cat("Regions covered:\n")
  for (r in sort(unique(df_wide$region))) {
    cat(sprintf("  - %s\n", r))
  }

  return(df_wide)
}

# ==============================================================================
# PART 3: LOAD POPULATION PROJECTIONS
# ==============================================================================

load_population_projections <- function(filepath = 'elementary_children_by_region_year.csv') {
  cat("\n", rep("=", 70), "\n", sep = "")
  cat("Loading Population Projections\n")
  cat(rep("=", 70), "\n\n", sep = "")

  df <- read_csv(filepath, show_col_types = FALSE) %>%
    rename(
      region = Region,
      year = Year,
      children_6_10 = Children_6_10
    )

  df$year <- as.numeric(df$year)

  cat(sprintf("Population projections: %d rows\n", nrow(df)))
  cat(sprintf("Years: %d - %d\n", min(df$year), max(df$year)))
  cat(sprintf("Regions: %d\n", n_distinct(df$region)))

  return(df)
}

# ==============================================================================
# PART 4: MERGE DATA
# ==============================================================================

merge_data <- function(school_df, pop_df) {
  cat("\n", rep("=", 70), "\n", sep = "")
  cat("Merging Datasets\n")
  cat(rep("=", 70), "\n\n", sep = "")

  # Full outer join
  merged <- full_join(school_df, pop_df, by = c("region", "year"))

  # Add projection indicator
  merged$proj <- ""
  merged$proj[is.na(merged$scuole) & merged$year >= 2023] <- "BSL"

  cat(sprintf("Merged data: %d rows\n", nrow(merged)))
  cat(sprintf("Historical records (with school data): %d\n",
              sum(!is.na(merged$scuole))))
  cat(sprintf("Projection records (population only): %d\n",
              sum(merged$proj == "BSL")))

  return(merged)
}

# ==============================================================================
# PART 5: CALCULATE RATIO PROJECTIONS
# ==============================================================================

calculate_ratio_projections <- function(df) {
  cat("\n", rep("=", 70), "\n", sep = "")
  cat("Calculating School Projections (Ratio Method)\n")
  cat(rep("=", 70), "\n\n", sep = "")

  results <- list()

  for (reg in sort(unique(df$region))) {
    cat(sprintf("Processing: %s\n", reg))

    region_df <- df %>%
      filter(region == reg) %>%
      arrange(year)

    # Check if we have historical data post-1990
    historical <- region_df %>%
      filter(!is.na(scuole), year > 1990)

    if (nrow(historical) == 0) {
      cat("  ⚠ No historical data available\n\n")
      next
    }

    # Use children_6_10 as proxy for studenti in projection years
    region_df$studenti_proj <- ifelse(is.na(region_df$studenti),
                                      region_df$children_6_10,
                                      region_df$studenti)

    # Calculate ratio for historical data
    region_df$ratio <- region_df$studenti / region_df$scuole

    # Calculate percentiles
    ratio_values <- region_df$ratio[!is.na(region_df$ratio)]
    ratio_min <- min(ratio_values, na.rm = TRUE)
    ratio_med <- median(ratio_values, na.rm = TRUE)
    ratio_max <- max(ratio_values, na.rm = TRUE)

    cat(sprintf("  Ratio - Min: %.1f, Median: %.1f, Max: %.1f\n\n",
                ratio_min, ratio_med, ratio_max))

    # Project schools using ratio
    region_df$ratio_hat <- ratio_med
    region_df$ratio_lcl <- ratio_min
    region_df$ratio_ucl <- ratio_max

    # For historical data, use observed values
    hist_mask <- !is.na(region_df$scuole)
    region_df$ratio_hat[hist_mask] <- region_df$ratio[hist_mask]
    region_df$ratio_lcl[hist_mask] <- region_df$ratio[hist_mask]
    region_df$ratio_ucl[hist_mask] <- region_df$ratio[hist_mask]

    # Calculate projected schools
    region_df$scuole_hat <- region_df$studenti_proj / region_df$ratio_hat
    region_df$scuole_lcl <- region_df$studenti_proj / region_df$ratio_ucl
    region_df$scuole_ucl <- region_df$studenti_proj / region_df$ratio_lcl

    # Preserve historical values
    region_df$scuole_hat[hist_mask] <- region_df$scuole[hist_mask]
    region_df$scuole_lcl[hist_mask] <- region_df$scuole[hist_mask]
    region_df$scuole_ucl[hist_mask] <- region_df$scuole[hist_mask]

    results[[reg]] <- region_df
  }

  # Combine all regions
  final_df <- bind_rows(results)

  cat(sprintf("✓ Projections calculated for %d regions\n",
              n_distinct(final_df$region)))

  return(final_df)
}

# ==============================================================================
# PART 6: CALCULATE DECLINE STATISTICS
# ==============================================================================

calculate_decline_statistics <- function(df) {
  cat("\n", rep("=", 70), "\n", sep = "")
  cat("Calculating Decline Statistics\n")
  cat(rep("=", 70), "\n\n", sep = "")

  stats <- df %>%
    filter(year %in% c(2022, 2050, 2080)) %>%
    select(region, year, scuole_hat) %>%
    pivot_wider(names_from = year, values_from = scuole_hat,
                names_prefix = "schools_") %>%
    mutate(
      change_2050 = schools_2050 - schools_2022,
      pct_change_2050 = (change_2050 / schools_2022) * 100,
      change_2080 = schools_2080 - schools_2022,
      pct_change_2080 = (change_2080 / schools_2022) * 100
    ) %>%
    arrange(pct_change_2050)

  cat("Top 10 regions with largest decline by 2050:\n")
  print(head(stats %>% select(region, pct_change_2050), 10), n = 10)

  return(stats)
}

# ==============================================================================
# PART 7: SAVE RESULTS
# ==============================================================================

save_results <- function(df, stats_df) {
  cat("\n", rep("=", 70), "\n", sep = "")
  cat("Saving Results\n")
  cat(rep("=", 70), "\n\n", sep = "")

  # Save projections
  write_csv(df, "school_projections_by_region_R.csv")
  cat("✓ Saved projections to: school_projections_by_region_R.csv\n")

  # Save statistics
  write_csv(stats_df, "regional_school_decline_statistics_R.csv")
  cat("✓ Saved statistics to: regional_school_decline_statistics_R.csv\n")

  # Create summary table
  summary_table <- stats_df %>%
    select(region, schools_2022, schools_2050, pct_change_2050,
           schools_2080, pct_change_2080) %>%
    mutate(across(starts_with("schools_"), round, 0)) %>%
    mutate(across(starts_with("pct_"), round, 1))

  write_csv(summary_table, "regional_school_summary_table_R.csv")
  cat("✓ Saved summary table to: regional_school_summary_table_R.csv\n")
}

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

main <- function() {
  cat("\n")
  cat(rep("=", 70), "\n", sep = "")
  cat("REGIONAL SCHOOL PROJECTIONS FOR ITALY\n")
  cat("R Implementation\n")
  cat(rep("=", 70), "\n\n", sep = "")

  # Step 1: Process school data
  school_df <- process_school_data('elementari.csv')

  # Step 2: Load population projections
  pop_df <- load_population_projections('elementary_children_by_region_year.csv')

  # Step 3: Merge datasets
  merged_df <- merge_data(school_df, pop_df)

  # Step 4: Calculate projections
  final_df <- calculate_ratio_projections(merged_df)

  # Step 5: Calculate decline statistics
  stats_df <- calculate_decline_statistics(final_df)

  # Step 6: Save results
  save_results(final_df, stats_df)

  cat("\n", rep("=", 70), "\n", sep = "")
  cat("Analysis Complete!\n")
  cat(rep("=", 70), "\n\n", sep = "")

  return(list(projections = final_df, statistics = stats_df))
}

# Run main function if script is executed directly
if (!interactive()) {
  result <- main()
}
