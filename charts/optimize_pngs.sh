#!/bin/bash
# This script finds all PNG files under the current directory and optimizes them for the web by:
#   • Converting them to an 8-bit color palette using pngquant (quality range 80-100),
#   • Further optimizing the compression with optipng,
# processing files concurrently with GNU Parallel.
#
# Requirements:
#   • pngquant (https://pngquant.org/)
#   • optipng (http://optipng.sourceforge.net/)
#   • GNU Parallel

# Check if pngquant is installed
if ! command -v pngquant &> /dev/null; then
  echo "Error: pngquant is not installed. Please install pngquant and try again."
  exit 1
fi

# Check if optipng is installed
if ! command -v optipng &> /dev/null; then
  echo "Error: optipng is not installed. Please install optipng and try again."
  exit 1
fi

# Check if GNU Parallel is installed
if ! command -v parallel &> /dev/null; then
  echo "Error: GNU Parallel is not installed. Please install GNU Parallel and try again."
  exit 1
fi

echo "Optimizing PNG files with pngquant and optipng in parallel..."

# Find all PNG files recursively and process each file in parallel.
find . -type f -iname "*.png" | parallel -j+0 '
  echo "Processing: {}"
  # Create a temporary file name for pngquant output.
  tmp_file="{}.tmp"
  if pngquant --quality=80-100 --force --output "$tmp_file" "{}"; then
    mv "$tmp_file" "{}"
    optipng -o2 "{}"
  else
    echo "pngquant failed for {}"
    rm -f "$tmp_file"
  fi
'

echo "PNG optimization complete."
