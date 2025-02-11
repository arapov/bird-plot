import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.patches import FancyBboxPatch

from ..config import load_config
from .base import add_bird_images, add_date, add_quadrants, setup_plot

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# TODO: make relative
def add_quadrant_titles(ax: Axes) -> None:
    """Add titles to the quadrants."""
    titles = [
        (12.5, 24, "Supportive & Caring"),  # Top-Right
        (-12.5, -24, "Controlling & Forceful"),  # Bottom-Right
        (-12.5, 24, "Talkative & Dramatic"),  # Top-Left
        (12.5, -24, "Analytical & Logical"),  # Bottom-Left
    ]

    for x, y, text in titles:
        ax.text(x, y, text, fontsize=12, ha="center", va="center")


# TODO: make relative
def add_axis_labels(ax: Axes) -> None:
    """Add descriptive labels to the axes."""
    labels = [
        (-0.02, 0.5, "Confident, Assertive, Bold", 90),  # Left Y-axis
        (0.5, 1.01, "Warm & Friendly, People-oriented", 0),  # Top X-axis
        (1.01, 0.5, "Shy, Non-assertive, Retiring", 270),  # Right Y-axis
        (0.5, -0.02, "Cold & Aloof, Task-oriented", 0),  # Bottom X-axis
    ]

    for x, y, text, rotation in labels:
        plt.text(
            x,
            y,
            text,
            transform=ax.transAxes,
            rotation=rotation,
            va="center",
            ha="center",
        )


def add_name_boxes(ax: Axes, df: pd.DataFrame) -> None:
    """Add names in rounded boxes to the plot."""
    for _, row in df.iterrows():
        text = f"{row['Name']} {row['Note']}"
        text_length = len(text)
        box_width = max(8, text_length * 0.4)
        box_height = 1

        box = FancyBboxPatch(
            (float(row["X"]) - box_width / 2, float(row["Y"]) - box_height / 2),
            width=box_width,
            height=box_height,
            boxstyle="round,pad=0.3",
            edgecolor="lightblue",
            facecolor="lightblue",
            alpha=0.8,
        )
        ax.add_patch(box)
        ax.text(
            float(row["X"]),
            float(row["Y"]),
            text,
            fontsize=10,
            ha="center",
            va="center",
            color="black",
        )


def add_grid(ax: Axes) -> None:
    # Add grid lines
    ax.axhline(0, color="gray", linewidth=0.5, linestyle="--")
    ax.axvline(0, color="gray", linewidth=0.5, linestyle="--")


def scatter_chart(df: pd.DataFrame, filename: Path, config_path: Path = Path("config.toml")) -> None:
    """Create a scatter plot of personality distributions.

    Args:
        df: DataFrame containing personality data points
        filename: Path where the chart should be saved
        config_path: Path to the TOML configuration file (defaults to config.toml)

    Raises:
        Exception: For any errors during chart creation
    """
    fig = None
    try:
        # Load configuration settings from TOML file
        config = load_config(config_path)

        # Create and configure the matplotlib figure and axes
        fig, ax = setup_plot(config)

        # Add chart components in layers:
        # 1. Background elements
        add_grid(ax)  # Add grid lines
        add_quadrants(ax, config)  # Add quadrant labels/divisions
        add_bird_images(ax, config)  # Add bird images if configured
        add_quadrant_titles(ax)  # Add quadrant titles
        add_axis_labels(ax)  # Add X and Y axis labels

        # 2. Data visualization elements
        add_name_boxes(ax, df)  # Add name boxes

        # 3. Metadata and title elements
        # Add current date to plot
        add_date(ax)

        # Set chart title
        plt.title(
            "Personality Distribution (Bird Parameters)",
            fontsize=14,
            fontweight="bold",
            y=1.03,
        )

        # Save the chart to file
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        logger.info(f"Plot saved to {filename}")

    except Exception as e:
        logger.error(f"Error creating scatter chart: {str(e)}")
        raise
    finally:
        if fig is not None:
            plt.close(fig)  # Close figure to free memory
