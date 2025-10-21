#!/usr/bin/env Rscript
#
# Download number of schools by region in Italy from 2010 onwards
# Data source: ISTAT (Italian National Institute of Statistics)
#

# Load required libraries
suppressPackageStartupMessages({
  if (!require("istat", quietly = TRUE)) {
    message("Installing istat package...")
    install.packages("istat")
    library(istat)
  } else {
    library(istat)
  }

  if (!require("tidyverse", quietly = TRUE)) {
    message("Installing tidyverse package...")
    install.packages("tidyverse")
    library(tidyverse)
  } else {
    library(tidyverse)
  }
})

# Main function to download and process school data
main <- function() {
  cat("=" %R% 70 %R% "\n")
  cat("Downloading Schools by Region Data from ISTAT\n")
  cat("=" %R% 70 %R% "\n\n")

  cat("Dataset: Number of schools by region in Italy\n")
  cat("Source: ISTAT\n")
  cat("Period: 2010 onwards\n\n")

  # Download data from ISTAT
  cat("Downloading data from ISTAT...\n")

  tryCatch({
    schools_data <- get_istatdata(
      agencyId = "IT1",
      dataset_id = "52_1044_DF_DCIS_SCUOLE_5",
      version = "1.0",
      start = NULL,
      end = NULL,
      recent = FALSE,
      csv = TRUE,
      xlsx = FALSE
    )

    cat("✓ Data downloaded successfully!\n\n")

    # Display structure of downloaded data
    cat("Data structure:\n")
    cat(sprintf("  Total rows: %d\n", nrow(schools_data)))
    cat(sprintf("  Total columns: %d\n", ncol(schools_data)))
    cat("\nColumn names:\n")
    print(colnames(schools_data))

    # Display first few rows
    cat("\n\nFirst few rows of data:\n")
    print(head(schools_data, 10))

    # Try to identify the year column (common names: Anno, ANNO, Year, TIME_PERIOD, etc.)
    year_col <- NULL
    possible_year_cols <- c("TIME_PERIOD", "Anno", "ANNO", "Year", "YEAR", "time_period", "anno")

    for (col in possible_year_cols) {
      if (col %in% colnames(schools_data)) {
        year_col <- col
        break
      }
    }

    if (!is.null(year_col)) {
      cat(sprintf("\n✓ Year column identified: '%s'\n", year_col))

      # Filter for 2010 onwards
      schools_data_filtered <- schools_data %>%
        mutate(year_numeric = as.numeric(as.character(.data[[year_col]]))) %>%
        filter(!is.na(year_numeric), year_numeric >= 2010)

      cat(sprintf("✓ Filtered for years >= 2010: %d rows\n", nrow(schools_data_filtered)))

      # Display year range
      cat(sprintf("  Year range: %d - %d\n",
                  min(schools_data_filtered$year_numeric, na.rm = TRUE),
                  max(schools_data_filtered$year_numeric, na.rm = TRUE)))

      # Save filtered data
      output_file <- "schools_by_region_2010_onwards.csv"
      write_csv(schools_data_filtered, output_file)
      cat(sprintf("\n✓ Filtered data saved to: %s\n", output_file))

    } else {
      cat("\n⚠ Could not automatically identify year column.\n")
      cat("  Saving all data without filtering by year.\n")
      schools_data_filtered <- schools_data
    }

    # Save raw data
    output_file_raw <- "schools_by_region_raw.csv"
    write_csv(schools_data, output_file_raw)
    cat(sprintf("✓ Raw data saved to: %s\n", output_file_raw))

    # Try to display summary by region if region column exists
    region_col <- NULL
    possible_region_cols <- c("ITTER107", "Territorio", "TERRITORIO", "Region", "REGION",
                             "Regione", "REGIONE", "territorio", "regione")

    for (col in possible_region_cols) {
      if (col %in% colnames(schools_data)) {
        region_col <- col
        break
      }
    }

    if (!is.null(region_col) && !is.null(year_col)) {
      cat(sprintf("\n✓ Region column identified: '%s'\n", region_col))

      # Get value column (usually named Value, VALORE, OBS_VALUE, etc.)
      value_col <- NULL
      possible_value_cols <- c("Value", "VALUE", "OBS_VALUE", "Valore", "VALORE",
                              "value", "valore", "obs_value")

      for (col in possible_value_cols) {
        if (col %in% colnames(schools_data_filtered)) {
          value_col <- col
          break
        }
      }

      if (!is.null(value_col)) {
        cat(sprintf("✓ Value column identified: '%s'\n", value_col))

        cat("\n\nSummary by region (most recent year):\n")

        summary_recent <- schools_data_filtered %>%
          mutate(value_numeric = as.numeric(as.character(.data[[value_col]]))) %>%
          group_by(.data[[region_col]]) %>%
          filter(.data[[year_col]] == max(.data[[year_col]], na.rm = TRUE)) %>%
          summarise(
            Latest_Year = first(.data[[year_col]]),
            Number_of_Schools = sum(value_numeric, na.rm = TRUE),
            .groups = "drop"
          ) %>%
          arrange(desc(Number_of_Schools))

        print(summary_recent, n = nrow(summary_recent))
      }
    }

    cat("\n" %R% rep("=", 70) %R% "\n")
    cat("Download and processing complete!\n")
    cat(rep("=", 70) %R% "\n")

    invisible(schools_data_filtered)

  }, error = function(e) {
    cat("\n✗ Error downloading data from ISTAT:\n")
    cat(sprintf("  %s\n\n", e$message))
    cat("Possible solutions:\n")
    cat("  1. Check your internet connection\n")
    cat("  2. Verify the dataset_id is correct\n")
    cat("  3. Check if ISTAT API is accessible\n")
    cat("  4. Try installing the latest version of istat package:\n")
    cat("     install.packages('istat')\n\n")

    return(NULL)
  })
}

# Define %R% operator for string repetition (if not already defined)
if (!exists("%R%")) {
  `%R%` <- function(x, y) {
    if (is.character(x) && is.numeric(y)) {
      paste(rep(x, y), collapse = "")
    } else if (is.numeric(x) && is.character(y)) {
      paste(rep(y, x), collapse = "")
    } else {
      stop("Invalid arguments for %R%")
    }
  }
}

# Run main function
if (!interactive()) {
  result <- main()
}
