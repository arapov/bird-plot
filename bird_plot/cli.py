import argparse
import os
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
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
        print(f"Error: Could not parse CSV file '{file_path}'. Check its format.")
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


def calculate_team_average(df: pd.DataFrame) -> dict:
    """Calculate the team average scores."""
    categories = ["Owl", "Dove", "Peacock", "Eagle"]
    avg_scores = {cat: df[cat].mean() for cat in categories}
    avg_scores["Name"] = "Team Average"
    avg_scores["Note"] = "Team Average Profile"
    return avg_scores


def generate_team_average_radar(df: pd.DataFrame) -> None:
    """Generate a single radar chart showing only the team average."""
    team_avg = calculate_team_average(df)
    output_filename = "radar_chart_team_average.png"
    radar_chart(team_avg, Path(output_filename))


def generate_radar_charts(df: pd.DataFrame) -> None:
    """Generate individual and comparison radar charts for all entries."""

    # Calculate team average
    team_avg = calculate_team_average(df)

    # Generate individual radar charts
    for _, row in df.iterrows():
        person_data = row.to_dict()
        output_filename = f"radar_chart_{person_data['Name']}.png"
        radar_chart(person_data, Path(output_filename))

        # Individual vs Team Average comparison
        output_filename = f"radar_chart_comparison_{person_data['Name']}_vs_TeamAvg.png"
        radar_chart(person_data, Path(output_filename), data2=team_avg)

    # Generate comparison radar charts for all possible pairs
    for (idx1, row1), (idx2, row2) in combinations(df.iterrows(), 2):
        person1_data = row1.to_dict()
        person2_data = row2.to_dict()
        output_filename = f"radar_chart_comparison_{person1_data['Name']}_{person2_data['Name']}.png"
        radar_chart(person1_data, Path(output_filename), data2=person2_data)


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

    def sigmoid_scale(series):
        # Use tanh to smoothly compress values to [-1, 1], then scale to ±25
        return 25 * np.tanh(series / series.abs().max())

    df["X"] = sigmoid_scale(df["X"])
    df["Y"] = sigmoid_scale(df["Y"])

    if args.graph_type == "radar":
        generate_radar_charts(df)
        generate_team_average_radar(df)
    else:  # scatter
        output_filename = "scatter_chart_all.png"
        scatter_chart(df, Path(output_filename))


if __name__ == "__main__":
    main()
