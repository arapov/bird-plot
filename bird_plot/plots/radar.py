import logging
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import Circle

from ..config import load_config
from .base import add_bird_images, add_date, add_quadrants, setup_plot

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def calculate_angles(categories: List[str], values: List[float]) -> Tuple[np.ndarray, np.ndarray]:
    """Calculate angles and values for the radar plot.

    Args:
        categories: List of category names to be displayed on the radar plot
        values: List of numerical values corresponding to each category

    Returns:
        tuple: (angles, values) where:
            - angles: numpy array of angles (in radians) for each category
            - values: numpy array of values with first value repeated at end

    Note:
        The function adds the first value/angle at the end of each array
        to create a closed polygon effect in the radar plot.
    """

    num_categories = len(categories)

    # Generate evenly spaced angles for each category
    # Starts at -π/4 (45° counterclockwise) and goes around the circle
    # endpoint=False ensures we don't duplicate the last point
    angles = np.linspace(-np.pi / 4, 2 * np.pi - np.pi / 4, num_categories, endpoint=False)

    # Convert values to numpy array
    values_array = np.array(values)

    # Add the first angle to the end to close the circular plot
    angles = np.concatenate((angles, [angles[0]]))
    # Add the first value to the end to close the polygon
    values_array = np.concatenate((values_array, [values_array[0]]))

    return angles, values_array


def add_labels(
    ax: Axes,
    angles: np.ndarray,
    values: np.ndarray,
) -> None:
    """Add numerical value labels to each point on the radar plot.

    Args:
        ax: The matplotlib axes object to draw on
        angles: Array of angles (in radians) for each point
        values: Array of numerical values to be displayed as labels

    Note:
        - Labels are offset slightly from their points for better visibility
        - The last value is skipped since it's a duplicate of the first (closing point)
        - Labels are positioned using trigonometric calculations for proper placement
    """

    if len(values) > 0:
        # Calculate offset distance for labels (10% of maximum value)
        # This prevents labels from overlapping with the plot lines
        offset = 0.1 * max(values)

        # Iterate through all values except the last (which is a duplicate)
        for i, value in enumerate(values[:-1]):
            # Calculate the point position using polar to cartesian conversion
            x = np.cos(angles[i]) * value  # x = r * cos(θ)
            y = np.sin(angles[i]) * value  # y = r * sin(θ)

            # Calculate perpendicular offset for label positioning
            # Uses rotated vector (-sin, cos) for perpendicular direction
            perp_x = -np.sin(angles[i]) * offset
            perp_y = np.cos(angles[i]) * offset

            # Add text label at the calculated position
            # Centered both horizontally and vertically
            ax.text(x + perp_x, y + perp_y, str(value), ha="center", va="center")


def add_grid(ax: Axes, config: Dict) -> None:
    """Add grid lines to the radar plot for better readability.

    Args:
        ax: The matplotlib axes object to draw on
        config: Dictionary containing chart configuration parameters including:
            - 'max_value': Maximum value for the grid extent
            - 'grid_step': Spacing between concentric grid circles
    """

    # Get the maximum value from config to determine grid size
    max_value = config["chart"]["max_value"]

    # Add diagonal grid lines (X-shaped)
    # First diagonal: bottom-left to top-right
    ax.plot(
        [-max_value, max_value],
        [-max_value, max_value],
        "-",  #  solid line
        color="grey",
        linewidth=0.5,
    )
    # Second diagonal: top-left to bottom-right
    ax.plot(
        [-max_value, max_value],
        [max_value, -max_value],
        "-",  #  solid line
        color="grey",
        linewidth=0.5,
    )

    # Add horizontal and vertical axes through origin
    ax.axhline(0, color="k", linestyle="-", linewidth=0.5)  # horizontal line
    ax.axvline(0, color="k", linestyle="-", linewidth=0.5)  # vertical line

    # Add concentric circular grid lines
    # Creates circles at regular intervals defined by grid_step
    for i in range(0, max_value + 1, config["chart"]["grid_step"]):
        # Create a circle centered at origin (0,0) with radius i
        circle = Circle(
            (0, 0),
            i,
            fill=False,
            linestyle="--",  # dashed line
            alpha=0.2,
        )
        ax.add_artist(circle)  # add circle to plot


def plot(ax: Axes, angles: np.ndarray, values: np.ndarray) -> None:
    """Draw the main radar plot with points and filled area.

    Args:
        ax: The matplotlib axes object to draw on
        angles: Array of angles (in radians) for each point
        values: Array of values determining the distance from center for each point
    """

    # Convert from polar (angle/radius) to cartesian (x/y) coordinates
    # x = r * cos(θ) where r is value and θ is angle
    x_coords = np.cos(angles) * values
    # y = r * sin(θ) where r is value and θ is angle
    y_coords = np.sin(angles) * values

    # Plot markers at each data point
    ax.plot(
        x_coords,
        y_coords,
        "x",  # Use 'x' shaped markers
        markersize=5,
        color="black",
    )

    # Fill the polygon created by connecting all points
    # This creates the filled shape of a radar plot
    ax.fill(x_coords, y_coords)


def radar_chart(data: Dict, filename: Path, config_path: Path = Path("config.toml")) -> None:
    """Create a radar chart for personality data.

    Args:
        data: Dictionary containing personality scores and metadata
        filename: Path where the chart should be saved
        config_path: Path to the TOML configuration file (defaults to config.toml)

    Raises:
        FileNotFoundError: If config file is not found
        Exception: For any other errors during chart creation
    """
    fig = None
    try:
        # Load configuration settings from TOML file
        config = load_config(config_path)

        # The order is critical for angle calculations:
        # Starting at -π/2 and going clockwise:
        # Owl (bottom right) → Dove (top right) → Peacock (top left) → Eagle (bottom left)
        ordered_categories = ["Owl", "Dove", "Peacock", "Eagle"]
        values = [data[cat] for cat in ordered_categories]
        angles, values = calculate_angles(ordered_categories, values)

        # Create and configure the matplotlib figure and axes
        fig, ax = setup_plot(config)

        # Add chart components in layers:
        # 1. Background elements
        add_grid(ax, config)  # Add grid lines
        add_quadrants(ax, config)  # Add quadrant labels/divisions
        add_bird_images(ax, config)  # Add bird images if configured

        # 2. Data visualization elements
        plot(ax, angles, values)  # Draw the main radar plot
        add_labels(ax, angles, values)  # Add value labels

        # 3. Metadata and title elements
        # Add current date to plot
        add_date(ax)
        # Set chart title using name and note from data
        plt.title(
            f"{data['Name']} {data['Note']}",
            fontsize=14,
            fontweight="bold",
        )

        # Save the chart to file
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        logger.info(f"Plot saved to {filename}")

    except Exception as e:
        # Log any errors and re-raise them
        logger.error(f"Error creating radar chart: {str(e)}")
        raise
    finally:
        plt.close(fig)  # Close figure to free memory
