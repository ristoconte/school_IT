#!/usr/bin/env Rscript
#
# Count elementary school age children (6-10 years) per Italian region per year
#

# Load required libraries
library(tidyverse)

# Function to extract region name from filename
extract_region_name <- function(filename) {
  # Pattern: it-Popolazione_per_eta_-_Regione_<RegionName>.csv
  region <- str_match(filename, "Regione_(.+)\\.csv$")[, 2]
  if (!is.na(region)) {
    region <- str_replace_all(region, "_", " ")
  }
  return(region)
}

# Function to process a single regional CSV file
process_regional_file <- function(filepath) {
  region_name <- extract_region_name(basename(filepath))

  if (is.na(region_name)) {
    message(sprintf("Could not extract region name from %s", filepath))
    return(NULL)
  }

  message(sprintf("Processing: %s", basename(filepath)))

  # Read CSV, skipping first 2 metadata rows
  df <- read_delim(
    filepath,
    delim = ";",
    skip = 2,
    locale = locale(encoding = "UTF-8"),
    show_col_types = FALSE
  )

  # Clean column names (remove BOM and extra whitespace)
  colnames(df) <- str_trim(colnames(df))
  colnames(df) <- str_replace_all(colnames(df), "^\uFEFF", "")

  # Filter for ages 6-10 (elementary school age)
  elementary_ages <- df %>%
    filter(Età %in% c(6, 7, 8, 9, 10))

  # Group by year and sum the median scenario values
  result <- elementary_ages %>%
    group_by(Anno) %>%
    summarise(Children_6_10 = sum(`Scenario mediano`, na.rm = TRUE), .groups = "drop") %>%
    mutate(Region = region_name) %>%
    select(Region, Year = Anno, Children_6_10)

  return(result)
}

# Main function
main <- function() {
  cat("Processing Italian regional population data...\n")
  cat("Counting elementary school age children (ages 6-10) per region per year\n\n")

  # Find all regional CSV files
  csv_files <- list.files(
    pattern = "^it-Popolazione_per_eta_-_Regione_.*\\.csv$",
    full.names = TRUE
  )

  if (length(csv_files) == 0) {
    stop("Error: No regional CSV files found!")
  }

  cat(sprintf("Found %d regional files to process\n\n", length(csv_files)))

  # Process all files
  all_results <- map_dfr(csv_files, process_regional_file)

  if (nrow(all_results) == 0) {
    stop("Error: No data was processed successfully!")
  }

  # Sort by region and year
  all_results <- all_results %>%
    arrange(Region, Year)

  # Save to CSV
  output_file <- "elementary_children_by_region_year_R.csv"
  write_csv(all_results, output_file)

  cat(sprintf("\n✓ Successfully created: %s\n", output_file))
  cat(sprintf("✓ Total records: %d\n", nrow(all_results)))
  cat(sprintf("✓ Regions covered: %d\n", n_distinct(all_results$Region)))
  cat(sprintf("✓ Years covered: %d - %d\n",
              min(all_results$Year),
              max(all_results$Year)))

  # Display sample of results
  cat("\nSample of results:\n")
  print(head(all_results, 10), n = 10)

  # Display summary statistics for 2024
  cat("\n\nSummary by region (2024):\n")
  summary_2024 <- all_results %>%
    filter(Year == 2024) %>%
    arrange(desc(Children_6_10))

  print(summary_2024, n = nrow(summary_2024))

  invisible(all_results)
}

# Run main function
if (!interactive()) {
  main()
}
