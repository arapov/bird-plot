import argparse
import os
import sys
from pathlib import Path

import pandas as pd

from .plots.radar import radar_chart
from .plots.scatter import scatter_chart

GRAPH_TYPES = ["radar", "scatter"]
DEFAULT_DATA_FILE = "data.csv"


def load_csv_data(file_path):
    """Load and validate CSV data from the given file path."""
    if not os.path.exists(file_path):
        print(f"Error: CSV file '{file_path}' not found!")
        sys.exit(1)

    try:
        return pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        print(f"Error: CSV file '{file_path}' is empty.")
        sys.exit(1)
    except pd.errors.ParserError:
        print(
            f"Error: Could not parse CSV file '{file_path}'. Check its format."
        )
        sys.exit(1)


def calculate_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate X and Y coordinates for the biplot."""
    try:
        df["X"] = (df["Dove"] + df["Owl"]) - (df["Peacock"] + df["Eagle"])
        df["Y"] = (df["Peacock"] + df["Dove"]) - (df["Eagle"] + df["Owl"])
        return df
    except KeyError as e:
        print(f"Error: Missing required column in CSV: {e}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate bird plot charts.")
    parser.add_argument(
        "--data",
        default=DEFAULT_DATA_FILE,
        help=f"Path to the CSV data file (default: {DEFAULT_DATA_FILE}).",
    )
    parser.add_argument(
        "--graph-type",
        choices=GRAPH_TYPES,
        default="scatter",
        help="Type of graph to generate (radar or scatter).",
    )
    args = parser.parse_args()

    # Load and process data
    df = load_csv_data(args.data)
    df = calculate_coordinates(df)

    # Calculate X and Y coordinates for the biplot.
    df["X"] = (df["Dove"] + df["Owl"]) - (df["Peacock"] + df["Eagle"])
    df["Y"] = (df["Peacock"] + df["Dove"]) - (df["Eagle"] + df["Owl"])

    if args.graph_type == "radar":
        for _, row in df.iterrows():
            person_data = row.to_dict()
            output_filename = f"radar_chart_{person_data['Name']}.png"
            radar_chart(person_data, Path(output_filename))
    else:  # scatter
        output_filename = "scatter_chart_all.png"
        scatter_chart(df, Path(output_filename))


if __name__ == "__main__":
    main()
