import argparse
import os
import sys
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

from .config import load_config
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


def calculate_team_average(df: pd.DataFrame) -> dict:
    """Calculate the team average scores."""
    categories = ["Owl", "Dove", "Peacock", "Eagle"]
    avg_scores = {cat: df[cat].mean() for cat in categories}
    avg_scores["Name"] = "Team Average"
    avg_scores["Note"] = "Team Average Profile"
    return avg_scores


def generate_team_average_radar(df: pd.DataFrame, config: Dict) -> None:
    """Generate a single radar chart showing only the team average."""
    # Get base output directory from config
    output_base = Path(config["paths"]["output"])
    output_base.mkdir(exist_ok=True)
    team_avg = calculate_team_average(df)
    output_filename = output_base / "radar_chart_team_average.png"
    radar_chart(team_avg, Path(output_filename), config)


def generate_radar_charts(df: pd.DataFrame, config: Dict) -> None:
    """Generate individual and comparison radar charts for all entries."""

    # Get base output directory from config
    output_base = Path(config["paths"]["output"])
    output_base.mkdir(exist_ok=True)

    # Calculate team average
    team_avg = calculate_team_average(df)

    # Generate individual radar charts
    for _, row in df.iterrows():
        person_data = row.to_dict()
        person_name = person_data["Name"]

        # Create person's directory if it doesn't exist
        person_dir = output_base / person_name
        person_dir.mkdir(exist_ok=True)

        # Create comparison subdirectory
        compare_dir = person_dir / "compare"
        compare_dir.mkdir(exist_ok=True)

        # Individual radar chart
        output_filename = person_dir / f"radar_{person_name}.png"
        radar_chart(person_data, output_filename, config)

        # Individual vs Team Average comparison
        output_filename = compare_dir / "with_TeamAvg.png"
        radar_chart(person_data, output_filename, config, data2=team_avg)

        # Generate comparisons with all other people
        for _, other_row in df.iterrows():
            if other_row["Name"] != person_name:
                other_data = other_row.to_dict()
                output_filename = compare_dir / f"with_{other_data['Name']}.png"
                radar_chart(person_data, output_filename, config, data2=other_data)


def process_personality_data(data_file: str, config: Dict) -> pd.DataFrame:
    """Load and process personality data from CSV file."""
    # Load data
    df = load_csv_data(data_file)
    personality_cols = ["Dove", "Owl", "Peacock", "Eagle"]

    # Adjust scores - multiply max scores by 1.2
    max_scores = df[personality_cols].max(axis=1)
    df_adjusted = (
        df[personality_cols].where(~df[personality_cols].eq(max_scores, axis=0), df[personality_cols] * 1.2).astype(int)
    )

    # Calculate X and Y coordinates
    df["X"] = (df_adjusted["Dove"] + df_adjusted["Owl"]) - (df_adjusted["Peacock"] + df_adjusted["Eagle"])
    df["Y"] = (df_adjusted["Peacock"] + df_adjusted["Dove"]) - (df_adjusted["Eagle"] + df_adjusted["Owl"])

    # Scale coordinates
    def sigmoid_scale(series):
        # Use tanh to smoothly compress values to [-1, 1], then scale to ±max_value
        return config["chart"]["max_value"] * np.tanh(series / series.abs().max())

    df["X"] = sigmoid_scale(df["X"])
    df["Y"] = sigmoid_scale(df["Y"])

    return df


def main() -> None:
    config = load_config()

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
    df = process_personality_data(args.data, config)

    if args.graph_type == "radar":
        generate_radar_charts(df, config)
        generate_team_average_radar(df, config)
    else:  # scatter
        # Get base output directory from config
        output_base = Path(config["paths"]["output"])
        output_base.mkdir(exist_ok=True)
        output_filename = output_base / "scatter_chart_all.png"
        scatter_chart(df, Path(output_filename), config)


if __name__ == "__main__":
    main()
