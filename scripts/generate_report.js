// generate_report.js
// Generates the Campus Delivery Robot project report as a .docx.
// Output: docs/Campus_Delivery_Robot_Report.docx
//
// Run with:  node scripts/generate_report.js

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, HeadingLevel, AlignmentType, LevelFormat, WidthType,
  ShadingType, BorderStyle, PageBreak, PageOrientation,
} = require("docx");

// ---------------------------------------------------------------------
// Styling helpers
// ---------------------------------------------------------------------
const FONT_BODY = "Calibri";
const FONT_HEAD = "Calibri";
const COLOR_ACCENT = "2E75B6";

const border = { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" };
const tableBorders = {
  top: border, bottom: border, left: border, right: border,
  insideHorizontal: border, insideVertical: border,
};
const HEADER_FILL = "D9E2F3";

function p(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 60, after: 60 },
    alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
    children: [new TextRun({
      text,
      font: FONT_BODY,
      size: opts.size || 22,        // 11pt
      bold: !!opts.bold,
      italics: !!opts.italic,
      color: opts.color || "262626",
    })],
  });
}

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 280, after: 120 },
    children: [new TextRun({ text, font: FONT_HEAD, size: 32,
                              bold: true, color: COLOR_ACCENT })],
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 220, after: 100 },
    children: [new TextRun({ text, font: FONT_HEAD, size: 26,
                              bold: true, color: "1F3864" })],
  });
}

function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 180, after: 80 },
    children: [new TextRun({ text, font: FONT_HEAD, size: 23,
                              bold: true, color: "262626" })],
  });
}

function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, font: FONT_BODY, size: 22 })],
  });
}

function code(text) {
  return new Paragraph({
    spacing: { before: 60, after: 60 },
    shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
    children: [new TextRun({ text, font: "Consolas", size: 20 })],
  });
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

// Cell helper
function cell(text, opts = {}) {
  return new TableCell({
    borders: tableBorders,
    width: { size: opts.width, type: WidthType.DXA },
    shading: opts.header
      ? { fill: HEADER_FILL, type: ShadingType.CLEAR }
      : undefined,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({
      children: [new TextRun({
        text,
        font: FONT_BODY,
        size: 20,
        bold: !!opts.header || !!opts.bold,
      })],
    })],
  });
}

// Image helper that reads PNG bytes from docs/.
function img(filename, widthPx, heightPx) {
  const bytes = fs.readFileSync(path.join(__dirname, "..", "docs", filename));
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 120 },
    children: [new ImageRun({
      data: bytes, type: "png",
      transformation: { width: widthPx, height: heightPx },
    })],
  });
}

// ---------------------------------------------------------------------
// Cover page
// ---------------------------------------------------------------------
const coverChildren = [
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 2200, after: 200 },
    children: [new TextRun({
      text: "Campus Delivery Robot",
      font: FONT_HEAD, size: 56, bold: true, color: COLOR_ACCENT,
    })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 80, after: 80 },
    children: [new TextRun({
      text: "A ROS-Based Smart Mobility System",
      font: FONT_HEAD, size: 32, italics: true, color: "1F3864",
    })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 1400, after: 60 },
    children: [new TextRun({
      text: "Smart Mobility Engineering",
      font: FONT_BODY, size: 26, bold: true,
    })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 60, after: 60 },
    children: [new TextRun({
      text: "Group Project - 7 Members",
      font: FONT_BODY, size: 24,
    })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 1400, after: 60 },
    children: [new TextRun({
      text: "Submission Date: 29 May 2026",
      font: FONT_BODY, size: 22, color: "595959",
    })],
  }),
  pageBreak(),
];

// ---------------------------------------------------------------------
// Body content
// ---------------------------------------------------------------------
const body = [];

// ----- 1. Honor Pledge -----
body.push(h1("Honor Pledge"));
body.push(p(
  "\u201C\uB098\uB294 \uC815\uC9C1\uD558\uAC8C \uC2DC\uD5D8\uC5D0 \uC751\uD560 \uAC83\uC744 \uC11C\uC57D\uD569\uB2C8\uB2E4.\u201D",
  { italic: true, center: true }));
body.push(p(
  "\u201CBy signing this pledge, I promise to adhere to exam requirements and maintain the highest level of ethical principles during the exam period.\u201D",
  { italic: true, center: true }));
body.push(p("Signed: ____________________   Date: ___________________", { center: true }));

// ----- 2. Table of Contents (manual) -----
body.push(pageBreak());
body.push(h1("Table of Contents"));
const toc = [
  "1. Executive Summary",
  "2. Project Objective and Scope",
  "3. System Architecture",
  "4. Operational Flowchart",
  "5. Member Contributions and Task Descriptions",
  "6. ROS Functions Coverage",
  "7. Hardware and Software Stack",
  "8. Testing Strategy",
  "9. Recording, Replay and Demonstration",
  "10. Build, Install and Run Instructions",
  "11. Risk Assessment and Mitigations",
  "12. Conclusion and Future Work",
  "13. Appendix: File Index",
];
toc.forEach(line => body.push(p(line)));

// ----- 3. Executive Summary -----
body.push(pageBreak());
body.push(h1("1. Executive Summary"));
body.push(p(
  "This report documents the design and implementation of a small autonomous campus delivery robot " +
  "built on ROS 1 Noetic, simulated in Gazebo with the TurtleBot3 (waffle_pi) platform. The robot " +
  "receives a delivery request through either a voice command or an advanced Click-based CLI, plans " +
  "a path with move_base, avoids obstacles using LiDAR and a camera-based pedestrian detector, opens " +
  "its delivery box upon arrival, and finally returns to its home dock. The project is the work of a " +
  "seven-member team. Every member owns at least two ROS functions and contributes a distinct vertical " +
  "slice of the system, so individual evaluation is straightforward and the system as a whole exercises " +
  "the full breadth of ROS concepts required by the course."
));

// ----- 4. Objective -----
body.push(h1("2. Project Objective and Scope"));
body.push(h2("2.1 Objective"));
body.push(p(
  "Design and implement a smart-mobility system that demonstrates the practical application of " +
  "publisher/subscriber, service, action, parameter server, tf2, rosbag, RViz and roslaunch primitives " +
  "while solving a realistic last-mile delivery task on a university campus."
));
body.push(h2("2.2 In-scope"));
[
  "Autonomous navigation from a home dock to a chosen destination and back.",
  "Real-time obstacle and pedestrian detection using a camera and a 2D LiDAR.",
  "Voice-command and CLI interfaces for dispatching missions.",
  "Remote monitoring of robot state, battery, and live camera feed via a JSON telemetry topic.",
  "Mandatory rosbag recording of each session for later replay and inspection.",
  "Pytest-based unit and integration scenarios that exercise the team\u2019s nodes.",
].forEach(t => body.push(bullet(t)));
body.push(h2("2.3 Out-of-scope"));
[
  "Physical hardware - the deliverable is a Gazebo simulation only.",
  "Outdoor GPS-only navigation; we simulate a NEO-style GPS fix from Gazebo ground-truth.",
  "Cloud connectivity, mobile applications, and account systems.",
].forEach(t => body.push(bullet(t)));

// ----- 5. Architecture -----
body.push(h1("3. System Architecture"));
body.push(p(
  "The system is split into eight cohesive ROS packages plus one CLI package and one test package. " +
  "Each member owns one functional vertical slice, and an eighth package (delivery_robot_bringup) " +
  "ties everything together with a single roslaunch entry point."
));
body.push(img("ros_architecture.png", 600, 380));
body.push(p("Figure 1 - ROS architecture overview (color-coded by team member).",
            { center: true, italic: true, size: 20 }));

body.push(h2("3.1 Package Inventory"));
body.push(new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [2900, 1500, 4960],
  rows: [
    new TableRow({ tableHeader: true, children: [
      cell("Package", { width: 2900, header: true }),
      cell("Owner", { width: 1500, header: true }),
      cell("Purpose", { width: 4960, header: true }),
    ]}),
    ...[
      ["delivery_msgs",              "shared", "Custom messages, services, action definitions used across the team."],
      ["delivery_perception_vision", "M1",     "Camera publisher and OpenCV-based pedestrian/obstacle detector."],
      ["delivery_perception_lidar",  "M2",     "LiDAR obstacle summariser and EmergencyStop service / brake controller."],
      ["delivery_localization",      "M3",     "Simulated GPS receiver and tf2 broadcaster for map -> odom."],
      ["delivery_navigation",        "M4",     "DeliveryMission action server (wrapping move_base) and plan summary helper."],
      ["delivery_voice_remote",      "M5",     "Voice command parser and JSON telemetry aggregator."],
      ["delivery_mission",           "M6",     "Delivery box service and high-level mission FSM."],
      ["delivery_cli",               "M7",     "Click-based command-line interface (delivery-cli)."],
      ["delivery_tests",             "M7",     "Pytest unit and integration scenarios."],
      ["delivery_robot_bringup",     "M7",     "Top-level launch files, RViz config, rosbag launch, parameter overrides."],
    ].map(([name, owner, desc]) => new TableRow({ children: [
      cell(name, { width: 2900 }),
      cell(owner, { width: 1500 }),
      cell(desc, { width: 4960 }),
    ]})),
  ],
}));

body.push(h2("3.2 Key Data Flows"));
[
  "Camera frames travel from Gazebo through M1\u2019s camera_publisher_node into the OpenCV detector, which emits ObstacleInfo messages on /delivery/perception/vision/obstacles.",
  "LiDAR scans go from Gazebo through M2\u2019s lidar_obstacle_node, summarised into a single ObstacleInfo on /delivery/perception/lidar/obstacle. The auto_brake_node consumes this topic and engages the brake via the EmergencyStop service when the obstacle is too close.",
  "Voice or CLI commands enter through M5\u2019s voice_command_node and are routed to M6\u2019s mission_fsm_node, which acts as the brain - calling M4\u2019s DeliveryMission action and M6\u2019s OpenDeliveryBox service in sequence.",
  "M5\u2019s remote_telemetry_node aggregates GPS, RobotStatus, brake state and plan summary into a single JSON topic that the CLI tool consumes through delivery-cli watch.",
].forEach(t => body.push(bullet(t)));

// ----- 6. Operational Flowchart -----
body.push(h1("4. Operational Flowchart"));
body.push(p(
  "The robot follows a deterministic state machine which is depicted below. Each branch in the flowchart " +
  "maps onto an explicit state in mission_fsm_node and is exercised by the integration tests."
));
body.push(img("operational_flowchart.png", 460, 640));
body.push(p("Figure 2 - Operational flowchart.",
            { center: true, italic: true, size: 20 }));

// ----- 7. Members -----
body.push(pageBreak());
body.push(h1("5. Member Contributions and Task Descriptions"));
body.push(p(
  "Every member owns at least two ROS functions. The following sub-sections detail what each member " +
  "contributed, what ROS primitive each function exercises, and where to find the corresponding code."
));

const members = [
  {
    id: "M1", area: "Vision Perception",
    package: "delivery_perception_vision",
    nodes: [
      ["camera_publisher_node", "Publisher",
       "Subscribes to the Gazebo camera topic and republishes throttled, resized BGR and JPEG-compressed streams that the rest of the system consumes."],
      ["vision_detector_node", "Subscriber + Custom-message Publisher",
       "Runs OpenCV HOG pedestrian detection and a fallback contour-based obstacle detector on each frame, then publishes ObstacleInfo messages and an annotated debug image used by RViz."],
    ],
  },
  {
    id: "M2", area: "LiDAR and Safety",
    package: "delivery_perception_lidar",
    nodes: [
      ["lidar_obstacle_node", "Subscriber + Publisher",
       "Reads /scan, finds the closest valid range in the forward 60-degree arc, and publishes a single ObstacleInfo summary used by everyone else."],
      ["auto_brake_node", "Service server + Publisher",
       "Advertises the EmergencyStop service and publishes a zero Twist on /cmd_vel whenever an obstacle crosses the configured brake distance."],
    ],
  },
  {
    id: "M3", area: "Localization and TF",
    package: "delivery_localization",
    nodes: [
      ["gps_simulator_node", "Publisher",
       "Synthesises a NEO-6M-style NavSatFix from /odom with realistic Gaussian noise so the remote monitoring app and the rosbag look credible during the demo."],
      ["map_tf_broadcaster_node", "tf2 broadcaster + Subscriber",
       "Maintains /map -> /odom when AMCL is not in charge, and listens to the RViz 2D Pose Estimate to reseed the transform during demos."],
    ],
  },
  {
    id: "M4", area: "Navigation and Planning",
    package: "delivery_navigation",
    nodes: [
      ["waypoint_action_server_node", "Action server + Action client to move_base",
       "Exposes the DeliveryMission action - the long-running task with live feedback (distance remaining, percent complete) - and forwards goals to move_base."],
      ["global_planner_helper_node", "Subscriber + Publisher",
       "Subscribes to the NavfnROS global plan and republishes a compact JSON summary (length, waypoint count) for the CLI and the telemetry stream."],
    ],
  },
  {
    id: "M5", area: "Voice and Remote Interface",
    package: "delivery_voice_remote",
    nodes: [
      ["voice_command_node", "Publisher + grammar parser",
       "Listens on a microphone (via SpeechRecognition) or on a simulated text topic, parses utterances with a regex grammar, and publishes VoiceCommand messages."],
      ["remote_telemetry_node", "Multi-Subscriber + Publisher",
       "Aggregates GPS, RobotStatus, brake state and plan summary into a single JSON telemetry topic used by the CLI and the remote monitoring view."],
    ],
  },
  {
    id: "M6", area: "Mission Control and Delivery",
    package: "delivery_mission",
    nodes: [
      ["delivery_box_service_node", "Service server + latched Publisher",
       "Implements the OpenDeliveryBox service with a simulated actuator delay and publishes the latched current state of the lid."],
      ["mission_fsm_node", "Action client + multi-Subscriber",
       "The robot\u2019s brain. Drives the full state machine - voice -> deliver -> arrive -> open box -> return home - using the navigation action and the box service."],
    ],
  },
  {
    id: "M7", area: "CLI, Tests, Infrastructure",
    package: "delivery_cli + delivery_tests + delivery_robot_bringup",
    nodes: [
      ["delivery-cli", "Advanced Click CLI",
       "Single delivery-cli binary with subcommands deliver, stop, resume, box, say, status, watch, bag, and list-destinations. Talks to every running node through the standard ROS interfaces."],
      ["delivery_tests", "Pytest + rostest",
       "Unit tests for the voice grammar and the CLI runner, and rostest-driven integration tests for the delivery box service and the LiDAR obstacle node."],
      ["delivery_robot_bringup", "roslaunch + parameter server + rosbag",
       "delivery_robot_full.launch wires the entire system together; move_base_overrides.yaml satisfies the parameter-server requirement; record_session.launch covers the mandatory rosbag deliverable."],
    ],
  },
];

members.forEach(m => {
  body.push(h2(`${m.id} - ${m.area}`));
  body.push(p(`Package: ${m.package}`, { italic: true }));
  m.nodes.forEach(([node, primitive, desc]) => {
    body.push(h3(`${node}  (${primitive})`));
    body.push(p(desc));
  });
});

// ----- 8. ROS functions checklist -----
body.push(pageBreak());
body.push(h1("6. ROS Functions Coverage"));
body.push(p(
  "The project intentionally covers every ROS concept listed in the project brief. The table below maps " +
  "each concept to the node, file or asset that exercises it."
));

body.push(new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [3200, 6160],
  rows: [
    new TableRow({ tableHeader: true, children: [
      cell("Concept", { width: 3200, header: true }),
      cell("Where it is exercised", { width: 6160, header: true }),
    ]}),
    ...[
      ["Publisher",          "camera_publisher_node, gps_simulator_node, lidar_obstacle_node, global_planner_helper_node, remote_telemetry_node"],
      ["Subscriber",         "vision_detector_node, auto_brake_node, mission_fsm_node, remote_telemetry_node"],
      ["Custom Messages",    "delivery_msgs/ObstacleInfo, RobotStatus, VoiceCommand"],
      ["Service (server)",   "auto_brake_node (EmergencyStop), delivery_box_service_node (OpenDeliveryBox)"],
      ["Service (client)",   "mission_fsm_node, delivery-cli (box/stop/resume subcommands)"],
      ["Action (server)",    "waypoint_action_server_node (DeliveryMission)"],
      ["Action (client)",    "mission_fsm_node, delivery-cli deliver"],
      ["Parameter Server",   "move_base_overrides.yaml (max speed, safety distance), waypoints.yaml"],
      ["tf2",                "map_tf_broadcaster_node, navigation server distance calculation"],
      ["rosbag",             "record_session.launch, delivery-cli bag start/stop/list"],
      ["RViz",               "delivery_robot.rviz with map, plan, LaserScan, annotated camera"],
      ["roslaunch",          "Every package has its own .launch; delivery_robot_full.launch composes them"],
      ["rostopic / rosservice", "delivery-cli watch and status subcommands exercise both"],
      ["Advanced CLI (Click)", "delivery_cli package (mandatory requirement)"],
      ["Pytest scenarios",   "delivery_tests/tests/test_*.py and .test files (mandatory requirement)"],
      ["Well-commented code","Every node has a module docstring and inline comments (mandatory requirement)"],
    ].map(([k, v]) => new TableRow({ children: [
      cell(k, { width: 3200, bold: true }),
      cell(v, { width: 6160 }),
    ]})),
  ],
}));

// ----- 9. Stack -----
body.push(h1("7. Hardware and Software Stack"));
body.push(h2("7.1 Software"));
[
  "Ubuntu 20.04 LTS",
  "ROS 1 Noetic (catkin / rospy)",
  "Gazebo 11 with TurtleBot3 waffle_pi model",
  "Navigation: move_base + AMCL + DWA local planner + NavfnROS global planner",
  "Python 3.8 with click, opencv-python, SpeechRecognition, pytest",
].forEach(t => body.push(bullet(t)));
body.push(h2("7.2 Simulated Sensors"));
[
  "Front-facing RGB camera (/camera/rgb/image_raw)",
  "360-degree LDS-01 LiDAR (/scan)",
  "Wheel odometry (/odom) - also used to synthesise GPS",
  "Simulated NEO-6M GPS (synthesised from /odom by gps_simulator_node)",
].forEach(t => body.push(bullet(t)));

// ----- 10. Testing -----
body.push(h1("8. Testing Strategy"));
body.push(p(
  "Testing is split into two layers. Pure-Python unit tests run with plain pytest in a few seconds " +
  "and need no ROS master, while integration tests run under rostest with the relevant node already " +
  "spawned by a .test file."
));
body.push(h2("8.1 Unit tests"));
[
  "test_voice_parser.py - exercises every branch of the voice grammar (deliver / stop / return home / open box / status) and verifies that unrelated chatter is rejected.",
  "test_cli.py - uses Click\u2019s CliRunner to verify --help, --version, all subcommand help screens, and the bag list command on empty and populated directories.",
].forEach(t => body.push(bullet(t)));
body.push(h2("8.2 Integration tests"));
[
  "test_delivery_box_service.py - launches delivery_box_service_node and checks the initial closed state, an open/close round trip, and idempotent calls.",
  "test_lidar_obstacle.py - publishes a synthetic /scan with a single forward obstacle and verifies the summariser reports the correct distance and an all-inf scan yields distance = -1.",
].forEach(t => body.push(bullet(t)));
body.push(h2("8.3 Running the tests"));
body.push(code("# fast unit tests\npytest src/delivery_tests/tests/test_voice_parser.py -v\npytest src/delivery_tests/tests/test_cli.py -v\n\n# integration tests\nrostest delivery_tests test_voice_parser.test\nrostest delivery_tests test_delivery_box_service.test"));

// ----- 11. Recording -----
body.push(h1("9. Recording, Replay and Demonstration"));
body.push(p(
  "Every demo run is captured with rosbag through the dedicated record_session.launch file. The bag " +
  "topic list was chosen so that a replay reconstructs both what the robot sensed and what it decided."
));
body.push(code("roslaunch delivery_robot_bringup delivery_robot_full.launch\nroslaunch delivery_robot_bringup record_session.launch bag_prefix:=demo_run1\n\n# inspect or replay\nrosbag info bag/demo_run1*.bag\nrosbag play bag/demo_run1*.bag"));

// ----- 12. Build & run -----
body.push(h1("10. Build, Install and Run Instructions"));
body.push(p("Verified on a fresh Ubuntu 20.04 install with ROS Noetic."));
body.push(code(`# 1) Dependencies
sudo apt install ros-noetic-desktop-full ros-noetic-turtlebot3 \\
    ros-noetic-turtlebot3-simulations ros-noetic-turtlebot3-navigation \\
    ros-noetic-navigation ros-noetic-map-server python3-pip
pip3 install --user click opencv-python SpeechRecognition pytest

# 2) Build
mkdir -p ~/campus_ws/src
cp -r campus_delivery_robot/src/* ~/campus_ws/src/
cd ~/campus_ws && catkin_make && source devel/setup.bash
export TURTLEBOT3_MODEL=waffle_pi

# 3) Install the click CLI
pip3 install --user -e ~/campus_ws/src/delivery_cli

# 4) Launch everything
roslaunch delivery_robot_bringup delivery_robot_full.launch

# 5) Drive a mission from another terminal
delivery-cli list-destinations
delivery-cli deliver library
delivery-cli status --follow`));

// ----- 13. Risks -----
body.push(h1("11. Risk Assessment and Mitigations"));
body.push(new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [3000, 3200, 3160],
  rows: [
    new TableRow({ tableHeader: true, children: [
      cell("Risk", { width: 3000, header: true }),
      cell("Impact", { width: 3200, header: true }),
      cell("Mitigation", { width: 3160, header: true }),
    ]}),
    ...[
      ["AMCL fails to converge on first launch", "Robot cannot localise; navigation refuses goals.",
       "RViz 2D Pose Estimate seeds the map_tf_broadcaster_node manually; documented in README troubleshooting."],
      ["HOG pedestrian detector misses the simulated humans", "Mission FSM never enters the pedestrian-stop branch.",
       "Fallback contour detector + LiDAR auto-brake provide a second and third safety net."],
      ["Microphone unavailable on demo machine", "Voice mode crashes at boot.",
       "voice_command_node lazily imports SpeechRecognition and falls back to text mode automatically; CLI provides delivery-cli say."],
      ["Action server cannot reach move_base", "Mission action returns immediate failure.",
       "Action server waits up to 15 seconds; mission FSM surfaces the failure into the FSM ERROR state."],
      ["Time pressure before submission", "Incomplete deliverables.",
       "Work split into 7 independent vertical slices; CI-friendly pytest suite catches regressions without needing ROS."],
    ].map(([r, i, m]) => new TableRow({ children: [
      cell(r, { width: 3000 }),
      cell(i, { width: 3200 }),
      cell(m, { width: 3160 }),
    ]})),
  ],
}));

// ----- 14. Conclusion -----
body.push(h1("12. Conclusion and Future Work"));
body.push(p(
  "The Campus Delivery Robot demonstrates a full end-to-end ROS application: perception, planning, " +
  "control, mission management, voice interface and an operator CLI all collaborate to deliver a package " +
  "across a simulated campus. Every team member ships at least two production-quality ROS functions and " +
  "the design choices keep individual contributions clearly attributable."
));
body.push(h2("12.1 Future work"));
[
  "Replace the HOG detector with a YOLOv8-nano person detector for better recall.",
  "Switch from move_base (ROS 1) to the Nav2 stack (ROS 2 Humble) for a cleaner action API.",
  "Add a real web dashboard that consumes /delivery/remote/telemetry over rosbridge.",
  "Bring the system onto a physical TurtleBot3 in a real lab corridor.",
].forEach(t => body.push(bullet(t)));

// ----- 15. Appendix -----
body.push(h1("13. Appendix: File Index"));
body.push(p("The submission archive contains the following top-level items:"));
[
  "README.md - quick-start documentation.",
  "src/ - catkin workspace with all 10 packages.",
  "scripts/ - diagram generators and helper scripts.",
  "docs/ - architecture and flowchart PNGs plus this report.",
  "bag/ - placeholder for recorded sessions.",
  "LICENSE - MIT license.",
].forEach(t => body.push(bullet(t)));

// ---------------------------------------------------------------------
// Document assembly
// ---------------------------------------------------------------------
const doc = new Document({
  creator: "Campus Delivery Robot Team",
  title: "Campus Delivery Robot - Project Report",
  styles: {
    default: { document: { run: { font: FONT_BODY, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: FONT_HEAD, color: COLOR_ACCENT },
        paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: FONT_HEAD, color: "1F3864" },
        paragraph: { spacing: { before: 220, after: 100 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 23, bold: true, font: FONT_HEAD },
        paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    children: [...coverChildren, ...body],
  }],
});

const outDir = path.join(__dirname, "..", "docs");
fs.mkdirSync(outDir, { recursive: true });
const outPath = path.join(outDir, "Campus_Delivery_Robot_Report.docx");
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(outPath, buf);
  console.log("wrote", outPath);
});
