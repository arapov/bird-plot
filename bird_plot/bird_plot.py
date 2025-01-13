import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import sys
import os
from dotenv import load_dotenv

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

def main():
    # Read data from CSV (specified in .env or passed as a command-line argument)
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = os.getenv("CSV_FILE_PATH", "data.csv")

    if not os.path.exists(file_path):
        print(f"CSV file '{file_path}' not found!")
        sys.exit(1)

    # Check if interactive plotting is enabled (command-line flag or environment variable)
    interactive_mode = os.getenv("INTERACTIVE_PLOT", "false").lower() == "true"
    if "--interactive" in sys.argv:
        interactive_mode = True

    # Load data
    df = pd.read_csv(file_path)

    # Calculate X and Y positions for the plot
    df["X"] = (df["Dove"] + df["Owl"]) - (df["Peacock"] + df["Eagle"])
    df["Y"] = (df["Peacock"] + df["Dove"]) - (df["Eagle"] + df["Owl"])

    # Plot
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.axhline(0, color='gray', linewidth=0.5, linestyle='--')
    ax.axvline(0, color='gray', linewidth=0.5, linestyle='--')

    # Add compact rounded boxes for each dot
    for i, row in df.iterrows():
        # Combine name and note for text
        text = f"{row['Name']} {row['Note']}"
        text_length = len(text)

        # Enhanced width calculation for better scaling
        box_width = max(6, text_length * 0.25)  # Minimum width of 6; scales better with text length
        box_height = 1  # Fixed compact height

        # Draw the rounded box
        box = FancyBboxPatch(
            (row["X"] - box_width / 2, row["Y"] - box_height / 2),  # Bottom-left corner of the box
            width=box_width,  # Width based on text length
            height=box_height,  # Fixed height for compactness
            boxstyle="round,pad=0.3",  # Rounded corners with slight padding
            edgecolor='lightblue',
            facecolor='lightblue',
            alpha=0.8
        )
        ax.add_patch(box)

        # Add the text inside the box
        ax.text(
            row["X"], row["Y"], text, fontsize=10, ha='center', va='center', color='black'
        )

    # Set fixed axis limits to ±25
    ax.set_xlim(-25, 25)
    ax.set_ylim(-25, 25)
    plt.title("Personality Distribution (Bird Parameters)", fontsize=14)
    plt.xlabel("Dove & Owl (+) vs Peacock & Eagle (-)")
    plt.ylabel("Peacock & Dove (+) vs Eagle & Owl (-)")
    ax.set_aspect('equal', adjustable='box')

    # Add bird images to the corners, twice as big, sticking to corners
    add_bird_image(ax, "birds/peacock.png", -25, 25, zoom=0.2)  # Top-left corner
    add_bird_image(ax, "birds/eagle.png", -25, -25, zoom=0.2)  # Bottom-left corner
    add_bird_image(ax, "birds/dove.png", 25, 25, zoom=0.2)    # Top-right corner
    add_bird_image(ax, "birds/owl.png", 25, -25, zoom=0.2)    # Bottom-right corner

    # Save the plot to a file
    output_path = os.getenv("OUTPUT_FILE_PATH", "output_plot.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Plot saved to {output_path}")

    # Show legend, grid, and plot interactively if enabled
    if interactive_mode:
        plt.legend()
        plt.grid(alpha=0.3)
        plt.show()

if __name__ == "__main__":
    main()
