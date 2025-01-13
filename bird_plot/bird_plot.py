import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import sys
import os
import argparse
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def add_bird_image(ax, img_path, x, y, zoom=0.2):
    """Add a bird image to the plot."""
    if os.path.exists(img_path):
        img = plt.imread(img_path)
        imagebox = OffsetImage(img, zoom=zoom)
        ab = AnnotationBbox(imagebox, (x, y), frameon=False, box_alignment=(0.5, 0.5))
        ax.add_artist(ab)
    else:
        print(f"Warning: Image not found at {img_path}")

def create_square_radar_chart(data, filename):
    categories = ['Dove', 'Owl', 'Peacock', 'Eagle']
    values = [data[cat] for cat in categories]
    num_categories = len(categories)

    angles = np.linspace(-np.pi / 4, 2 * np.pi - np.pi / 4, num_categories, endpoint=False)
    values = values + values[:1]
    angles = np.concatenate((angles, [angles[0]]))

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.plot(np.cos(angles) * values, np.sin(angles) * values, 'o', linewidth=2, markersize=2, color='black')
    ax.fill(np.cos(angles) * values, np.sin(angles) * values )

    max_value = 25
    ax.set_aspect('equal', adjustable='box')

    # Add diagonal axes (black, full length, thinner)
    ax.plot([-max_value, max_value], [-max_value, max_value], 'k-', linewidth=0.1)  # Diagonal 1
    ax.plot([-max_value, max_value], [max_value, -max_value], 'k-', linewidth=0.1)  # Diagonal 2

    # Add horizontal and vertical lines
    ax.axhline(0, color='k', linestyle='-', linewidth=0.75)
    ax.axvline(0, color='k', linestyle='-', linewidth=0.75)

    # Add colored quadrants
    quadrant_rects = [
        Rectangle((-29, 0), 29, 29, facecolor='lightgreen', alpha=0.2, edgecolor=None, zorder=-1), # Top-Right
        Rectangle((-29, -29), 29, 29, facecolor='lightcoral', alpha=0.2, edgecolor=None, zorder=-1), # Bottom-Right
        Rectangle((0, 0), 29, 29, facecolor='lightskyblue', alpha=0.2, edgecolor=None, zorder=-1), # Top-Left
        Rectangle((0, -29), 29, 29, facecolor='khaki', alpha=0.2, edgecolor=None, zorder=-1), # Bottom-Left
    ]
    for rect in quadrant_rects:
        ax.add_patch(rect)

    # Add date
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    ax.text(1.05, -0.1, f"Generated: {date_string}", transform=ax.transAxes, ha='right')

    # Add labels to the dots
    offset = 0.1 * max(values)  # Adjust offset as needed
    for i, value in enumerate(values[:-1]):
        x = np.cos(angles[i]) * value
        y = np.sin(angles[i]) * value
        # Calculate perpendicular offset
        perp_x = -np.sin(angles[i]) * offset
        perp_y = np.cos(angles[i]) * offset
        ax.text(x + perp_x, y + perp_y, str(value), ha='center', va='center')

    # Add radial gridlines
    for i in range(0, max_value + 1, 5):
        circle = plt.Circle((0, 0), i, fill=False, linestyle='--', alpha=0.3)
        ax.add_artist(circle)

    ax.set_title(f"Personality Square Chart - {data['Name']} - {data['Note']}")
    ax.set_xticks([])
    ax.set_yticks([])

    #ax.set_xlim([-max_value * 1.2, max_value * 1.2])
    #ax.set_ylim([-max_value * 1.2, max_value * 1.2])

    # Add bird images to the corners, sticking to corners
    add_bird_image(ax, "birds/peacock.png", -27, 27, zoom=0.2) # Top-left corner
    add_bird_image(ax, "birds/eagle.png", -27, -27, zoom=0.2)  # Bottom-left corner
    add_bird_image(ax, "birds/dove.png", 27, 27, zoom=0.2)     # Top-right corner
    add_bird_image(ax, "birds/owl.png", 27, -27, zoom=0.2)     # Bottom-right corner

    plt.savefig(filename, dpi=300)
    plt.close(fig)

def create_scatter_plot(df, filename):
    # Check if interactive plotting is enabled (command-line flag or environment variable)
    interactive_mode = os.getenv("INTERACTIVE_PLOT", "false").lower() == "true"

    # Plot
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.axhline(0, color='gray', linewidth=0.5, linestyle='--')
    ax.axvline(0, color='gray', linewidth=0.5, linestyle='--')

    # Add quadrant titles
    ax.text(12.5, 24, "Supportive & Caring", fontsize=12, ha='center', va='center') # Top-Right
    ax.text(-12.5, -24, "Controlling & Forceful", fontsize=12, ha='center', va='center') # Bottom-Right
    ax.text(-12.5, 24, "Talkative & Dramatic", fontsize=12, ha='center', va='center') # Top-Left
    ax.text(12.5, -24, "Analytical & Logical", fontsize=12, ha='center', va='center') # Bottom-Left

    # Add colored quadrants
    quadrant_rects = [
        Rectangle((-25, 0), 25, 25, facecolor='lightgreen', alpha=0.2, edgecolor=None, zorder=-1), # Top-Right
        Rectangle((-25, -25), 25, 25, facecolor='lightcoral', alpha=0.2, edgecolor=None, zorder=-1), # Bottom-Right
        Rectangle((0, 0), 25, 25, facecolor='lightskyblue', alpha=0.2, edgecolor=None, zorder=-1), # Top-Left
        Rectangle((0, -25), 25, 25, facecolor='khaki', alpha=0.2, edgecolor=None, zorder=-1), # Bottom-Left
    ]
    for rect in quadrant_rects:
        ax.add_patch(rect)

    # Add date
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    ax.text(1.05, -0.1, f"Generated: {date_string}", transform=ax.transAxes, ha='right')

    # Add names in rounded boxes
    for i, row in df.iterrows():
        # Combine name and note for text
        text = f"{row['Name']} {row['Note']}"
        text_length = len(text)

        # Scaling calculation
        box_width = max(6, text_length * 0.25)  # Minimum width of 6; scales with text length
        box_height = 1  # Fixed compact height

        # Draw the rounded box
        box = FancyBboxPatch(
            (row["X"] - box_width / 2, row["Y"] - box_height / 2),  # Bottom-left corner of the box
            width=box_width,  # Width based on text length
            height=box_height,  # Fixed height
            boxstyle="round,pad=0.3",  # Rounded corners
            edgecolor='lightblue',
            facecolor='lightblue',
            alpha=0.8
        )
        ax.add_patch(box)

        # Add the text to the box
        ax.text(
            row["X"], row["Y"], text, fontsize=10, ha='center', va='center', color='black'
        )

    # Set fixed axis limits to ±25
    ax.set_xlim(-25, 25)
    ax.set_ylim(-25, 25)
    ax.set_xticks([])  # Remove x-axis ticks
    ax.set_yticks([])  # Remove y-axis ticks
    ax.set_aspect('equal', adjustable='box')

    # Describe
    plt.title("Personality Distribution (Bird Parameters)", fontsize=14, fontweight='bold', y=1.03)
    plt.text(-0.02, 0.5, "Confident, Assertive, Bold", transform=plt.gca().transAxes, rotation=90, va='center')  #Right Y-axis label
    plt.text(0.5, 1.01, "Warm & Friendly, People-oriented", transform=plt.gca().transAxes, ha='center') # Bottom X-axis label
    plt.text(1.01, 0.5, "Shy, Non-assertive, Retiring", transform=plt.gca().transAxes, rotation=270, va='center')  #Right Y-axis label
    plt.text(0.5, -0.02, "Coll & Aloof, Task-oriented", transform=plt.gca().transAxes, ha='center') # Bottom X-axis label

    # Add bird images to the corners, sticking to corners
    add_bird_image(ax, "birds/peacock.png", -25, 25, zoom=0.2) # Top-left corner
    add_bird_image(ax, "birds/eagle.png", -25, -25, zoom=0.2)  # Bottom-left corner
    add_bird_image(ax, "birds/dove.png", 25, 25, zoom=0.2)     # Top-right corner
    add_bird_image(ax, "birds/owl.png", 25, -25, zoom=0.2)     # Bottom-right corner

    if interactive_mode:
        # Show legend, grid, and plot interactively
        plt.legend()
        plt.grid(alpha=0.3)
        plt.show()
    else:
        # Save the plot to a file
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        print(f"Plot saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Generate bird plot charts.")
    parser.add_argument("--data", default="data.csv", help="Path to the CSV data file (default: data.csv).")
    parser.add_argument("--graph-type", choices=["radar", "scatter"], default="scatter", help="Type of graph to generate (radar or scatter).")
    args = parser.parse_args()

    file_path = args.data
    graph_type = args.graph_type

    if not os.path.exists(file_path):
        print(f"Error: CSV file '{file_path}' not found!")
        sys.exit(1)

    try:
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        print(f"Error: CSV file '{file_path}' is empty.")
        sys.exit(1)
    except pd.errors.ParserError:
        print(f"Error: Could not parse CSV file '{file_path}'. Check its format.")
        sys.exit(1)

    # Calculate X and Y coordinates for the biplot.
    df["X"] = (df["Dove"] + df["Owl"]) - (df["Peacock"] + df["Eagle"])
    df["Y"] = (df["Peacock"] + df["Dove"]) - (df["Eagle"] + df["Owl"])

    if graph_type == "radar":
        for index, row in df.iterrows():
            person_data = row.to_dict()
            output_filename = f"radar_chart_{person_data['Name']}.png"
            create_square_radar_chart(person_data, output_filename)
    elif graph_type == "scatter":
        output_filename = "scatter_chart_all.png"
        create_scatter_plot(df, output_filename)
    else:
        print(f"Error: Invalid graph type '{graph_type}'. Choose from 'radar' or 'scatter'.")
        print("Use --help for more information.") # Suggest using --help if available.
        sys.exit(1)

if __name__ == "__main__":
    main()
