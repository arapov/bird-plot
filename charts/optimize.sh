#!/bin/bash
# This script finds all PNG files under the current directory,
# optimizes them for the web by:
#   • Stripping metadata,
#   • Resizing them to 33% of the original dimensions,
#   • Converting them to an 8-bit color depth,
# using GNU Parallel for concurrent processing.
#
# Requirements:
#   • ImageMagick (mogrify)
#   • GNU Parallel

# Check if mogrify is installed
if ! command -v mogrify &> /dev/null; then
  echo "Error: mogrify (ImageMagick) is not installed. Please install ImageMagick and try again."
  exit 1
fi

# Check if GNU Parallel is installed
if ! command -v parallel &> /dev/null; then
  echo "Error: GNU Parallel is not installed. Please install GNU Parallel and try again."
  exit 1
fi

echo "Finding and optimizing PNG files in parallel..."

# Find all PNG files (case-insensitive) and process each in parallel
find . -type f -iname "*.png" | parallel -j+0 '
  echo "Optimizing: {}";
  mogrify -strip -resize 33% -depth 8 "{}"
'

echo "PNG optimization complete."
