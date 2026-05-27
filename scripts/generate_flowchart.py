#!/usr/bin/env python3
"""
Generate the operational flowchart PNG for the Campus Delivery Robot.
Mirrors the team's hand-drawn flowchart, but cleaner for the report
and PowerPoint.
"""

import os

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon


def terminator(ax, x, y, text):
    """Oval shape - Start / End."""
    e = patches.Ellipse((x, y), 1.6, 0.6,
                         facecolor="#34495E",
                         edgecolor="#2C3E50")
    ax.add_patch(e)
    ax.text(x, y, text, ha="center", va="center",
            fontsize=10, color="white", weight="bold")


def process(ax, x, y, text, color="#3498DB"):
    """Rectangle - process step."""
    box = FancyBboxPatch((x - 1.3, y - 0.3), 2.6, 0.6,
                          boxstyle="round,pad=0.04",
                          facecolor=color, edgecolor="#2C3E50",
                          linewidth=1.3)
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center",
            fontsize=9, color="white", weight="bold")


def decision(ax, x, y, text, color="#E67E22"):
    """Diamond - decision."""
    pts = [(x, y + 0.55), (x + 1.4, y), (x, y - 0.55), (x - 1.4, y)]
    diamond = Polygon(pts, closed=True,
                       facecolor=color, edgecolor="#2C3E50",
                       linewidth=1.3)
    ax.add_patch(diamond)
    ax.text(x, y, text, ha="center", va="center",
            fontsize=8, color="white", weight="bold")


def io_block(ax, x, y, text, color="#9B59B6"):
    """Parallelogram - input/output."""
    pts = [(x - 1.4, y - 0.3), (x - 1.2, y + 0.3),
           (x + 1.4, y + 0.3), (x + 1.2, y - 0.3)]
    par = Polygon(pts, closed=True,
                   facecolor=color, edgecolor="#2C3E50",
                   linewidth=1.3)
    ax.add_patch(par)
    ax.text(x, y, text, ha="center", va="center",
            fontsize=9, color="white", weight="bold")


def arrow(ax, p1, p2, label=""):
    a = FancyArrowPatch(p1, p2, arrowstyle="-|>",
                         mutation_scale=14, linewidth=1.2,
                         color="#2C3E50")
    ax.add_patch(a)
    if label:
        mx, my = (p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0
        ax.text(mx + 0.15, my, label, fontsize=8,
                color="#2C3E50", weight="bold")


def main():
    fig, ax = plt.subplots(figsize=(11, 16), dpi=140)
    ax.set_xlim(-2, 12)
    ax.set_ylim(0, 22)
    ax.axis("off")

    ax.text(5, 21.4, "Campus Delivery Robot - Operational Flowchart",
            ha="center", fontsize=15, weight="bold", color="#2C3E50")

    # --- Main vertical column at x = 5 ---
    terminator(ax, 5, 20.5, "Start")
    io_block(ax, 5, 19.4, "Voice command received")
    process(ax, 5, 18.3, "Get GPS destination", "#3498DB")
    process(ax, 5, 17.2, "Calculate path (move_base)", "#3498DB")
    process(ax, 5, 16.1, "Move forward")
    decision(ax, 5, 14.7, "Obstacle\ndetected?")
    process(ax, 1.5, 14.7, "Avoid obstacle", "#E74C3C")
    decision(ax, 5, 12.7, "Pedestrian\ndetected?")
    process(ax, 1.5, 12.7, "Stop moving", "#E74C3C")
    process(ax, 5, 10.9, "Continue moving")
    decision(ax, 5, 9.3, "Reached\ndestination?")
    process(ax, 1.5, 9.3, "Keep navigating", "#F39C12")
    process(ax, 5, 7.3, "Open delivery box", "#27AE60")
    process(ax, 5, 6.0, "Wait for pickup")
    process(ax, 5, 4.7, "Close box & return home", "#27AE60")
    terminator(ax, 5, 3.2, "End")

    # --- Arrows on the main path ---
    arrow(ax, (5, 20.2), (5, 19.75))
    arrow(ax, (5, 19.1), (5, 18.65))
    arrow(ax, (5, 18.0), (5, 17.55))
    arrow(ax, (5, 16.9), (5, 16.45))
    arrow(ax, (5, 15.8), (5, 15.3))
    arrow(ax, (5, 14.1), (5, 13.3), "NO")
    arrow(ax, (5, 12.1), (5, 11.25), "NO")
    arrow(ax, (5, 10.6), (5, 9.9))
    arrow(ax, (5, 8.7), (5, 7.65), "YES")
    arrow(ax, (5, 6.95), (5, 6.35))
    arrow(ax, (5, 5.65), (5, 5.05))
    arrow(ax, (5, 4.35), (5, 3.55))

    # --- Side branches (YES) ---
    arrow(ax, (3.6, 14.7), (2.9, 14.7))      # obstacle yes
    ax.text(3.05, 15.0, "YES", fontsize=8, color="#2C3E50", weight="bold")
    arrow(ax, (1.5, 14.4), (1.5, 12.7))      # back-loop after avoid
    arrow(ax, (1.5, 12.7), (3.6, 12.7))      # rejoin into pedestrian decision

    arrow(ax, (3.6, 12.7), (2.9, 12.7))      # pedestrian yes
    ax.text(3.05, 13.0, "YES", fontsize=8, color="#2C3E50", weight="bold")
    arrow(ax, (1.5, 12.4), (1.5, 11.6))      # wait
    arrow(ax, (1.5, 11.6), (3.7, 10.9))      # rejoin continue moving

    # NO side for destination
    arrow(ax, (3.6, 9.3), (2.9, 9.3))
    ax.text(3.05, 9.6, "NO", fontsize=8, color="#2C3E50", weight="bold")
    arrow(ax, (1.5, 9.0), (1.5, 8.0))
    arrow(ax, (1.5, 8.0), (1.5, 14.4))       # loop back to before move

    # --- Legend / shape key ---
    legend_x = 9.0
    items = [
        ("Start / End",  "ellipse",   "#34495E"),
        ("Input / Output", "parallel", "#9B59B6"),
        ("Process",      "box",       "#3498DB"),
        ("Decision",     "diamond",   "#E67E22"),
        ("Safety action", "box",      "#E74C3C"),
        ("Delivery action", "box",    "#27AE60"),
    ]
    ax.text(legend_x, 20.5, "Legend",
            fontsize=11, weight="bold", color="#2C3E50")
    for i, (label, shape, color) in enumerate(items):
        y = 19.7 - i * 0.7
        if shape == "ellipse":
            ax.add_patch(patches.Ellipse((legend_x, y), 0.7, 0.35,
                                          facecolor=color, edgecolor="#2C3E50"))
        elif shape == "diamond":
            pts = [(legend_x, y + 0.25), (legend_x + 0.35, y),
                   (legend_x, y - 0.25), (legend_x - 0.35, y)]
            ax.add_patch(Polygon(pts, facecolor=color, edgecolor="#2C3E50"))
        elif shape == "parallel":
            pts = [(legend_x - 0.4, y - 0.15), (legend_x - 0.3, y + 0.15),
                   (legend_x + 0.4, y + 0.15), (legend_x + 0.3, y - 0.15)]
            ax.add_patch(Polygon(pts, facecolor=color, edgecolor="#2C3E50"))
        else:
            ax.add_patch(FancyBboxPatch((legend_x - 0.4, y - 0.15), 0.8, 0.3,
                                         boxstyle="round,pad=0.02",
                                         facecolor=color, edgecolor="#2C3E50"))
        ax.text(legend_x + 0.6, y, label,
                fontsize=9, va="center", color="#2C3E50")

    plt.tight_layout()
    out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         "..", "docs", "operational_flowchart.png"))
    plt.savefig(out, bbox_inches="tight", facecolor="white")
    print("wrote", out)


if __name__ == "__main__":
    main()
