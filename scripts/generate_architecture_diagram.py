#!/usr/bin/env python3
"""
Generate the ROS architecture diagram for the Campus Delivery Robot.
Outputs a PNG that the team can drop into the report and PowerPoint.

Run:
    python3 scripts/generate_architecture_diagram.py
"""

import os

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# ---------------------------------------------------------------------
# Colour palette - one colour per team member.
# ---------------------------------------------------------------------
COLOURS = {
    "M1": "#E74C3C",  # red    - vision
    "M2": "#E67E22",  # orange - lidar/safety
    "M3": "#F1C40F",  # yellow - localisation
    "M4": "#27AE60",  # green  - navigation
    "M5": "#3498DB",  # blue   - voice / remote
    "M6": "#9B59B6",  # purple - mission
    "M7": "#34495E",  # dark   - cli / infra
    "EXT": "#BDC3C7", # grey   - external (gazebo, move_base, etc)
}


def draw_node(ax, x, y, w, h, text, color, fontsize=8):
    """Draw a rounded rectangle representing a ROS node."""
    box = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                          boxstyle="round,pad=0.02,rounding_size=0.08",
                          linewidth=1.4,
                          edgecolor="#2C3E50",
                          facecolor=color,
                          alpha=0.92)
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center",
            fontsize=fontsize, color="white", weight="bold",
            wrap=True)


def draw_arrow(ax, p1, p2, label="", color="#2C3E50", style="solid"):
    """Draw a labelled arrow between two points."""
    arrow = FancyArrowPatch(p1, p2,
                             arrowstyle="-|>",
                             mutation_scale=14,
                             linewidth=1.1,
                             color=color,
                             linestyle=style,
                             alpha=0.85)
    ax.add_patch(arrow)
    if label:
        mx, my = (p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0
        ax.text(mx, my, label, fontsize=6.5,
                ha="center", va="center",
                color="#2C3E50",
                bbox=dict(facecolor="white",
                          edgecolor="none",
                          alpha=0.85,
                          pad=1.2))


def main():
    fig, ax = plt.subplots(figsize=(18, 12), dpi=140)
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12)
    ax.axis("off")

    # Title.
    ax.text(9, 11.5,
            "Campus Delivery Robot - ROS Architecture",
            ha="center", fontsize=18, weight="bold", color="#2C3E50")
    ax.text(9, 11.05,
            "7-member team, ROS 1 Noetic, TurtleBot3 / Gazebo",
            ha="center", fontsize=10, style="italic", color="#7F8C8D")

    # ------------------------------------------------------------------
    # External layer (top)
    # ------------------------------------------------------------------
    draw_node(ax, 2.0, 10.0, 2.6, 0.7, "Gazebo Simulator", COLOURS["EXT"])
    draw_node(ax, 5.5, 10.0, 2.6, 0.7, "TurtleBot3 (waffle_pi)", COLOURS["EXT"])
    draw_node(ax, 9.0, 10.0, 2.6, 0.7, "move_base + AMCL", COLOURS["EXT"])
    draw_node(ax, 12.5, 10.0, 2.6, 0.7, "RViz", COLOURS["EXT"])
    draw_node(ax, 15.8, 10.0, 3.0, 0.7, "rosbag recorder", COLOURS["EXT"])

    # ------------------------------------------------------------------
    # Sensor topics row (just under Gazebo)
    # ------------------------------------------------------------------
    ax.text(2.0, 9.3, "/camera/rgb/image_raw",
            ha="center", fontsize=7, color="#566573")
    ax.text(5.5, 9.3, "/scan   /odom   /tf",
            ha="center", fontsize=7, color="#566573")

    # ------------------------------------------------------------------
    # Member 1 - Vision (left column)
    # ------------------------------------------------------------------
    draw_node(ax, 2.0, 8.2, 3.2, 0.8,
              "M1  camera_publisher_node\n(pub /delivery/camera/image)",
              COLOURS["M1"])
    draw_node(ax, 2.0, 6.7, 3.2, 0.8,
              "M1  vision_detector_node\n(OpenCV HOG + obstacle)",
              COLOURS["M1"])

    draw_arrow(ax, (2.0, 9.65), (2.0, 8.6), "Image")
    draw_arrow(ax, (2.0, 7.8), (2.0, 7.1), "Image")

    # ------------------------------------------------------------------
    # Member 2 - LiDAR / safety
    # ------------------------------------------------------------------
    draw_node(ax, 5.5, 8.2, 3.2, 0.8,
              "M2  lidar_obstacle_node\n(/scan -> ObstacleInfo)",
              COLOURS["M2"])
    draw_node(ax, 5.5, 6.7, 3.2, 0.8,
              "M2  auto_brake_node\n(EmergencyStop service)",
              COLOURS["M2"])

    draw_arrow(ax, (5.5, 9.65), (5.5, 8.6), "LaserScan")
    draw_arrow(ax, (5.5, 7.8), (5.5, 7.1), "ObstacleInfo")

    # ------------------------------------------------------------------
    # Member 3 - Localisation
    # ------------------------------------------------------------------
    draw_node(ax, 9.0, 8.2, 3.2, 0.8,
              "M3  gps_simulator_node\n(NavSatFix on /delivery/gps/fix)",
              COLOURS["M3"], fontsize=7.5)
    draw_node(ax, 9.0, 6.7, 3.2, 0.8,
              "M3  map_tf_broadcaster\n(/map -> /odom tf2)",
              COLOURS["M3"])

    draw_arrow(ax, (6.8, 9.65), (8.5, 8.6), "Odometry")

    # ------------------------------------------------------------------
    # Member 4 - Navigation
    # ------------------------------------------------------------------
    draw_node(ax, 12.5, 8.2, 3.2, 0.8,
              "M4  waypoint_action_server\n(DeliveryMission action)",
              COLOURS["M4"])
    draw_node(ax, 12.5, 6.7, 3.2, 0.8,
              "M4  global_planner_helper\n(plan summary publisher)",
              COLOURS["M4"])

    draw_arrow(ax, (12.5, 9.65), (12.5, 8.6), "MoveBase goal", color="#27AE60")
    draw_arrow(ax, (10.6, 9.65), (12.5, 7.1), "/plan", color="#27AE60", style="dashed")

    # ------------------------------------------------------------------
    # Member 5 - Voice + Remote
    # ------------------------------------------------------------------
    draw_node(ax, 2.0, 4.5, 3.2, 0.8,
              "M5  voice_command_node\n(mic / text -> VoiceCommand)",
              COLOURS["M5"])
    draw_node(ax, 5.5, 4.5, 3.2, 0.8,
              "M5  remote_telemetry_node\n(JSON aggregator)",
              COLOURS["M5"])

    # ------------------------------------------------------------------
    # Member 6 - Mission control
    # ------------------------------------------------------------------
    draw_node(ax, 9.0, 4.5, 3.2, 0.8,
              "M6  mission_fsm_node\n(state machine + battery)",
              COLOURS["M6"])
    draw_node(ax, 12.5, 4.5, 3.2, 0.8,
              "M6  delivery_box_service\n(OpenDeliveryBox srv)",
              COLOURS["M6"])

    # ------------------------------------------------------------------
    # Member 7 - CLI + tests + bringup (bottom)
    # ------------------------------------------------------------------
    draw_node(ax, 5.5, 2.5, 4.2, 1.1,
              "M7  delivery-cli (click)\ndeliver / stop / box / say /\nwatch / bag / list-destinations",
              COLOURS["M7"])
    draw_node(ax, 11.0, 2.5, 4.2, 1.1,
              "M7  delivery_tests (pytest)\nvoice parser / box srv /\nlidar / CLI",
              COLOURS["M7"])
    draw_node(ax, 16.0, 2.5, 3.6, 1.1,
              "M7  bringup +\nrosbag launch +\nparameter server cfg",
              COLOURS["M7"])

    # ------------------------------------------------------------------
    # Cross-team data flows (mission FSM is the hub)
    # ------------------------------------------------------------------
    # Voice -> mission
    draw_arrow(ax, (3.6, 4.5), (7.4, 4.5), "VoiceCommand", color=COLOURS["M5"])

    # Vision -> mission (pedestrian)
    draw_arrow(ax, (2.0, 6.3), (8.0, 4.9), "ObstacleInfo (pedestrian)",
                color=COLOURS["M1"], style="dashed")

    # Lidar obstacle -> auto brake (already on same column) -> /cmd_vel
    draw_arrow(ax, (7.1, 6.7), (15.0, 10.0), "/cmd_vel (zero on brake)",
                color=COLOURS["M2"], style="dashed")

    # Mission -> navigation action server
    draw_arrow(ax, (10.6, 4.5), (11.5, 7.8), "DeliveryMission goal",
                color=COLOURS["M6"])

    # Mission -> delivery box
    draw_arrow(ax, (10.6, 4.5), (10.9, 4.5), "OpenDeliveryBox srv",
                color=COLOURS["M6"])

    # Status -> telemetry
    draw_arrow(ax, (9.0, 4.1), (5.5, 4.1), "RobotStatus",
                color=COLOURS["M6"])

    # Telemetry/status -> CLI
    draw_arrow(ax, (5.5, 4.1), (5.5, 3.1), "telemetry JSON",
                color=COLOURS["M5"])
    draw_arrow(ax, (9.0, 4.1), (10.0, 3.1), "RobotStatus",
                color=COLOURS["M6"])

    # CLI -> services / action
    draw_arrow(ax, (7.6, 2.5), (11.5, 4.1), "deliver / box / stop",
                color=COLOURS["M7"], style="dashed")

    # rosbag listens to many - draw a representative arrow
    draw_arrow(ax, (12.5, 7.8), (15.8, 9.65), "/move_base/*",
                color="#7F8C8D", style="dotted")
    draw_arrow(ax, (9.0, 4.9), (15.8, 9.65), "/delivery/*",
                color="#7F8C8D", style="dotted")

    # ------------------------------------------------------------------
    # Legend
    # ------------------------------------------------------------------
    legend_items = [
        ("Member 1 - Vision",         COLOURS["M1"]),
        ("Member 2 - LiDAR / Safety", COLOURS["M2"]),
        ("Member 3 - Localisation",   COLOURS["M3"]),
        ("Member 4 - Navigation",     COLOURS["M4"]),
        ("Member 5 - Voice / Remote", COLOURS["M5"]),
        ("Member 6 - Mission",        COLOURS["M6"]),
        ("Member 7 - CLI / Infra",    COLOURS["M7"]),
        ("External / ROS core",       COLOURS["EXT"]),
    ]
    for i, (label, color) in enumerate(legend_items):
        x = 0.4
        y = 0.9 - 0.18 * i
        rect = patches.Rectangle((x, y), 0.3, 0.15,
                                  facecolor=color,
                                  edgecolor="#2C3E50")
        ax.add_patch(rect)
        ax.text(x + 0.4, y + 0.075, label,
                fontsize=8, va="center", color="#2C3E50")

    plt.tight_layout()

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ros_architecture.png")
    plt.savefig(out_path, bbox_inches="tight",
                facecolor="white")
    print("wrote", out_path)


if __name__ == "__main__":
    main()
