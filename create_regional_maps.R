#!/usr/bin/env Rscript
#
# Create Regional Maps and Visualizations in R
# Generates maps showing school projections using shapefile
#

# Load required libraries
suppressPackageStartupMessages({
  library(tidyverse)
  library(sf)           # For spatial data
  library(ggplot2)
  library(scales)
  library(RColorBrewer)
  library(viridis)
})

# Shapefile COD_REG to region names mapping
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
# LOAD AND PREPARE DATA
# ==============================================================================

load_and_prepare_data <- function() {
  cat(rep("=", 70), "\n", sep = "")
  cat("Loading Data for Mapping\n")
  cat(rep("=", 70), "\n\n", sep = "")

  # Load shapefile
  cat("Loading shapefile...\n")
  gdf <- st_read('Reg01012022_g/Reg01012022_g_WGS84.shp', quiet = TRUE)
  cat(sprintf("  ✓ Loaded %d regions from shapefile\n", nrow(gdf)))

  # Load statistics
  cat("\nLoading statistics...\n")
  stats_df <- read_csv('regional_school_decline_statistics_R.csv',
                       show_col_types = FALSE)
  cat(sprintf("  ✓ Loaded statistics for %d regions\n", nrow(stats_df)))

  # Map COD_REG to region names
  gdf$region <- COD_REG_TO_REGION[as.character(gdf$COD_REG)]

  # Merge with statistics
  gdf <- gdf %>%
    left_join(stats_df, by = "region")

  cat(sprintf("\n  Regions in shapefile: %d\n", nrow(gdf)))
  cat(sprintf("  Regions with data: %d\n",
              sum(!is.na(gdf$pct_change_2050))))

  if (any(is.na(gdf$pct_change_2050))) {
    missing <- gdf$region[is.na(gdf$pct_change_2050)]
    cat(sprintf("\n  ⚠ Warning: %d regions missing data:\n",
                length(missing)))
    for (m in missing) {
      cat(sprintf("    - %s\n", m))
    }
  }

  return(gdf)
}

# ==============================================================================
# CREATE DIVERGING MAP (% CHANGE)
# ==============================================================================

create_diverging_map <- function(gdf, column, year, title, filename) {
  cat(sprintf("\nCreating map: %s...\n", title))

  # Get data range for symmetric scale
  data_range <- range(gdf[[column]], na.rm = TRUE)
  abs_max <- max(abs(data_range))

  # Create plot
  p <- ggplot(gdf) +
    geom_sf(aes(fill = .data[[column]]), color = "black", size = 0.3) +
    scale_fill_gradient2(
      low = "#d73027",
      mid = "#ffffbf",
      high = "#1a9850",
      midpoint = 0,
      limits = c(-abs_max, abs_max),
      name = "Change (%)",
      na.value = "lightgrey"
    ) +
    labs(title = title) +
    theme_void() +
    theme(
      plot.title = element_text(hjust = 0.5, face = "bold", size = 14),
      legend.position = "bottom",
      legend.key.width = unit(2, "cm"),
      legend.title = element_text(face = "bold")
    )

  # Save plot
  ggsave(paste0(filename, "_R.png"), p, width = 10, height = 12, dpi = 300)
  ggsave(paste0(filename, "_R.pdf"), p, width = 10, height = 12)
  cat(sprintf("  ✓ Saved: %s_R.png/pdf\n", filename))

  return(p)
}

# ==============================================================================
# CREATE ABSOLUTE MAP (NUMBER OF SCHOOLS)
# ==============================================================================

create_absolute_map <- function(gdf, column, year, title, filename) {
  cat(sprintf("\nCreating map: %s...\n", title))

  # Create plot
  p <- ggplot(gdf) +
    geom_sf(aes(fill = .data[[column]]), color = "black", size = 0.3) +
    scale_fill_viridis_c(
      option = "plasma",
      name = "Schools",
      na.value = "lightgrey",
      trans = "sqrt"  # Square root transform for better visualization
    ) +
    labs(title = title) +
    theme_void() +
    theme(
      plot.title = element_text(hjust = 0.5, face = "bold", size = 14),
      legend.position = "bottom",
      legend.key.width = unit(2, "cm"),
      legend.title = element_text(face = "bold")
    )

  # Save plot
  ggsave(paste0(filename, "_R.png"), p, width = 10, height = 12, dpi = 300)
  ggsave(paste0(filename, "_R.pdf"), p, width = 10, height = 12)
  cat(sprintf("  ✓ Saved: %s_R.png/pdf\n", filename))

  return(p)
}

# ==============================================================================
# CREATE CATEGORICAL MAP
# ==============================================================================

create_category_map <- function(gdf) {
  cat("\nCreating categorical map...\n")

  # Categorize regions
  gdf$category <- cut(
    gdf$pct_change_2050,
    breaks = c(-Inf, -10, 0, 20, 50, Inf),
    labels = c("Strong Decline (< -10%)",
               "Moderate Decline (0 to -10%)",
               "Moderate Growth (0 to 20%)",
               "Strong Growth (20 to 50%)",
               "Very Strong Growth (> 50%)"),
    right = FALSE
  )

  # Define colors
  category_colors <- c(
    "Strong Decline (< -10%)" = "#d73027",
    "Moderate Decline (0 to -10%)" = "#fc8d59",
    "Moderate Growth (0 to 20%)" = "#fee08b",
    "Strong Growth (20 to 50%)" = "#a6d96a",
    "Very Strong Growth (> 50%)" = "#1a9850"
  )

  # Create plot
  p <- ggplot(gdf) +
    geom_sf(aes(fill = category), color = "black", size = 0.3) +
    scale_fill_manual(
      values = category_colors,
      name = "Projection Category",
      na.value = "lightgrey"
    ) +
    labs(title = "Regional School Projections by 2050\nCategorical View") +
    theme_void() +
    theme(
      plot.title = element_text(hjust = 0.5, face = "bold", size = 14),
      legend.position = "right",
      legend.title = element_text(face = "bold")
    )

  # Save plot
  ggsave("regional_school_map_categorical_R.png", p,
         width = 12, height = 10, dpi = 300)
  ggsave("regional_school_map_categorical_R.pdf", p,
         width = 12, height = 10)
  cat("  ✓ Saved: regional_school_map_categorical_R.png/pdf\n")

  return(p)
}

# ==============================================================================
# CREATE TREND PLOTS
# ==============================================================================

create_trend_plots <- function() {
  cat("\nCreating trend plots...\n")

  # Load projection data
  proj_df <- read_csv('school_projections_by_region_R.csv',
                      show_col_types = FALSE)

  # Get top 5 regions by 2022 schools
  top_regions <- proj_df %>%
    filter(year == 2022, !is.na(scuole)) %>%
    arrange(desc(scuole)) %>%
    head(5) %>%
    pull(region)

  # Plot 1: Absolute schools
  p1 <- proj_df %>%
    filter(region %in% top_regions) %>%
    ggplot(aes(x = year, y = scuole_hat, color = region, group = region)) +
    geom_line(size = 1) +
    geom_point(data = . %>% filter(!is.na(scuole)),
               aes(y = scuole), size = 2) +
    geom_vline(xintercept = 2022, linetype = "dashed", alpha = 0.5) +
    scale_color_brewer(palette = "Set1", name = "Region") +
    labs(
      title = "Elementary School Projections by Region\n(Top 5 Regions)",
      x = "Year",
      y = "Number of Schools"
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(hjust = 0.5, face = "bold", size = 12),
      legend.position = "bottom"
    )

  ggsave("regional_school_trends_R.png", p1, width = 12, height = 6, dpi = 300)
  ggsave("regional_school_trends_R.pdf", p1, width = 12, height = 6)
  cat("  ✓ Saved: regional_school_trends_R.png/pdf\n")

  # Plot 2: Indexed to 2022
  baseline_2022 <- proj_df %>%
    filter(year == 2022, region %in% top_regions) %>%
    select(region, baseline = scuole)

  p2 <- proj_df %>%
    filter(region %in% top_regions) %>%
    left_join(baseline_2022, by = "region") %>%
    mutate(indexed = (scuole_hat / baseline) * 100) %>%
    ggplot(aes(x = year, y = indexed, color = region, group = region)) +
    geom_line(size = 1) +
    geom_vline(xintercept = 2022, linetype = "dashed", alpha = 0.5) +
    geom_hline(yintercept = 100, linetype = "dotted", alpha = 0.5) +
    scale_color_brewer(palette = "Set1", name = "Region") +
    labs(
      title = "Elementary School Projections - Indexed to 2022",
      x = "Year",
      y = "Index (2022 = 100)"
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(hjust = 0.5, face = "bold", size = 12),
      legend.position = "bottom"
    )

  ggsave("regional_school_trends_indexed_R.png", p2,
         width = 12, height = 6, dpi = 300)
  ggsave("regional_school_trends_indexed_R.pdf", p2,
         width = 12, height = 6)
  cat("  ✓ Saved: regional_school_trends_indexed_R.png/pdf\n")

  return(list(p1 = p1, p2 = p2))
}

# ==============================================================================
# MAIN FUNCTION
# ==============================================================================

main <- function() {
  cat("\n")
  cat(rep("=", 70), "\n", sep = "")
  cat("Regional School Projection Maps - R Implementation\n")
  cat(rep("=", 70), "\n\n", sep = "")

  # Load data
  gdf <- load_and_prepare_data()

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

  # Create trend plots
  create_trend_plots()

  cat("\n", rep("=", 70), "\n", sep = "")
  cat("Map Creation Complete!\n")
  cat(rep("=", 70), "\n\n", sep = "")

  cat("Generated files (R versions):\n")
  cat("  - regional_school_map_2050_R.png/pdf\n")
  cat("  - regional_school_map_2080_R.png/pdf\n")
  cat("  - regional_school_map_2022_absolute_R.png/pdf\n")
  cat("  - regional_school_map_2050_absolute_R.png/pdf\n")
  cat("  - regional_school_map_categorical_R.png/pdf\n")
  cat("  - regional_school_trends_R.png/pdf\n")
  cat("  - regional_school_trends_indexed_R.png/pdf\n\n")
}

# Run main function if script is executed directly
if (!interactive()) {
  main()
}
