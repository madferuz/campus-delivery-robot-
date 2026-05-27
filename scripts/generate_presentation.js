// generate_presentation.js
// Builds the Campus Delivery Robot project presentation as a .pptx
// using pptxgenjs. Output: docs/Campus_Delivery_Robot.pptx

const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";   // 13.3 x 7.5 inches
pres.title  = "Campus Delivery Robot";
pres.author = "Campus Delivery Robot Team";

// ---------------------------------------------------------------------
// Palette - "Midnight Executive" inspired but customised for robotics.
// ---------------------------------------------------------------------
const NAVY      = "1E2761";  // dominant dark
const NAVY_DARK = "13193F";
const ICE       = "CADCFC";  // soft secondary
const ACCENT    = "F96167";  // sharp accent for highlights
const WHITE     = "FFFFFF";
const MUTED     = "8A99C7";

// Member colours (consistent with the architecture diagram).
const MEMBER_COLORS = {
  M1: "E74C3C", M2: "E67E22", M3: "F1C40F", M4: "27AE60",
  M5: "3498DB", M6: "9B59B6", M7: "34495E",
};

// Slide dimensions for LAYOUT_WIDE.
const W = 13.3, H = 7.5;

// ---------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------
function lightSlide() {
  const s = pres.addSlide();
  s.background = { color: WHITE };
  return s;
}

function darkSlide() {
  const s = pres.addSlide();
  s.background = { color: NAVY };
  return s;
}

function slideHeader(slide, title, sub) {
  // Title
  slide.addText(title, {
    x: 0.6, y: 0.4, w: W - 1.2, h: 0.7,
    fontSize: 32, bold: true, fontFace: "Calibri",
    color: NAVY, margin: 0,
  });
  if (sub) {
    slide.addText(sub, {
      x: 0.6, y: 1.05, w: W - 1.2, h: 0.4,
      fontSize: 16, italic: true, fontFace: "Calibri",
      color: MUTED, margin: 0,
    });
  }
  // Slide-number pill bottom-right.
}

function pageNumber(slide, idx, total) {
  slide.addText(`${idx} / ${total}`, {
    x: W - 1.4, y: H - 0.5, w: 1.0, h: 0.3,
    fontSize: 10, color: MUTED, align: "right", fontFace: "Calibri",
  });
}

// ---------------------------------------------------------------------
// Build slides. We collect them in an array so we can stamp page
// numbers at the end with the correct total count.
// ---------------------------------------------------------------------
const slides = [];

// ------ Slide 1: Title --------------------------------------------------
{
  const s = darkSlide();

  // Accent shape - large rotated square as background motif.
  s.addShape(pres.shapes.RECTANGLE, {
    x: -1, y: -1, w: 4, h: 4, fill: { color: NAVY_DARK },
    rotate: 18, line: { color: NAVY_DARK },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: W - 3, y: H - 2.5, w: 5, h: 5, fill: { color: ACCENT, transparency: 70 },
    rotate: -12, line: { type: "none" },
  });

  s.addText("CAMPUS DELIVERY ROBOT", {
    x: 0.8, y: 2.4, w: W - 1.6, h: 1.0,
    fontSize: 52, bold: true, color: WHITE, fontFace: "Calibri",
    charSpacing: 4,
  });
  s.addText("A ROS-Based Smart Mobility System", {
    x: 0.8, y: 3.45, w: W - 1.6, h: 0.6,
    fontSize: 22, italic: true, color: ICE, fontFace: "Calibri",
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.85, y: 4.25, w: 0.6, h: 0.05, fill: { color: ACCENT },
    line: { type: "none" },
  });

  s.addText([
    { text: "Smart Mobility Engineering", options: { breakLine: true, bold: true } },
    { text: "Group Project · 7 Members", options: { breakLine: true } },
    { text: "Submission Date: 29 May 2026" },
  ], {
    x: 0.85, y: 4.45, w: W - 1.6, h: 1.2,
    fontSize: 16, color: ICE, fontFace: "Calibri",
    paraSpaceAfter: 4,
  });

  slides.push(s);
}

// ------ Slide 2: Agenda -------------------------------------------------
{
  const s = lightSlide();
  slideHeader(s, "Agenda");

  const items = [
    ["01", "Project Objective"],
    ["02", "System Architecture"],
    ["03", "Operational Flow"],
    ["04", "Member Contributions"],
    ["05", "ROS Functions Coverage"],
    ["06", "Demo & Recording"],
    ["07", "Testing Strategy"],
    ["08", "Q&A"],
  ];

  // Two-column grid of agenda items.
  items.forEach((item, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.6 + col * 6.3;
    const y = 1.9 + row * 1.2;

    s.addShape(pres.shapes.OVAL, {
      x, y, w: 0.9, h: 0.9, fill: { color: NAVY }, line: { type: "none" },
    });
    s.addText(item[0], {
      x, y, w: 0.9, h: 0.9,
      fontSize: 20, bold: true, color: WHITE,
      align: "center", valign: "middle", fontFace: "Calibri", margin: 0,
    });
    s.addText(item[1], {
      x: x + 1.15, y: y + 0.18, w: 5.0, h: 0.55,
      fontSize: 18, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
    });
  });

  slides.push(s);
}

// ------ Slide 3: Project Objective --------------------------------------
{
  const s = lightSlide();
  slideHeader(s, "01 · Project Objective",
              "Last-mile autonomous delivery on a university campus");

  // Two columns: left "What" with bullets, right stat callouts.
  s.addText("What we are building", {
    x: 0.6, y: 1.7, w: 7.0, h: 0.4,
    fontSize: 18, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
  });
  s.addText([
    { text: "A simulated TurtleBot3 that delivers packages between buildings",
      options: { bullet: true, breakLine: true } },
    { text: "Triggered by either a voice command or an advanced Click CLI",
      options: { bullet: true, breakLine: true } },
    { text: "Plans a path with move_base, avoids obstacles and pedestrians",
      options: { bullet: true, breakLine: true } },
    { text: "Opens its delivery box on arrival, then returns to home dock",
      options: { bullet: true, breakLine: true } },
    { text: "Records every session to a rosbag for later replay",
      options: { bullet: true } },
  ], {
    x: 0.6, y: 2.2, w: 7.0, h: 4.0,
    fontSize: 16, color: "262626", fontFace: "Calibri",
    paraSpaceAfter: 6,
  });

  // Right column - stat cards.
  const cards = [
    ["7",  "Team Members"],
    ["10", "ROS Packages"],
    ["14+", "ROS Functions"],
    ["4",  "Pytest Modules"],
  ];
  cards.forEach((c, i) => {
    const cx = 8.4 + (i % 2) * 2.3;
    const cy = 1.9 + Math.floor(i / 2) * 2.4;
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: cy, w: 2.1, h: 2.1,
      fill: { color: ICE }, line: { type: "none" },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: cy, w: 2.1, h: 0.08,
      fill: { color: ACCENT }, line: { type: "none" },
    });
    s.addText(c[0], {
      x: cx, y: cy + 0.3, w: 2.1, h: 1.0,
      fontSize: 48, bold: true, color: NAVY,
      align: "center", valign: "middle", fontFace: "Calibri", margin: 0,
    });
    s.addText(c[1], {
      x: cx, y: cy + 1.4, w: 2.1, h: 0.5,
      fontSize: 12, color: NAVY, align: "center", fontFace: "Calibri", margin: 0,
    });
  });

  slides.push(s);
}

// ------ Slide 4: Architecture diagram -----------------------------------
{
  const s = lightSlide();
  slideHeader(s, "02 · System Architecture",
              "10 ROS packages · 7-member vertical slices · ROS 1 Noetic");

  // Insert the architecture diagram. Slide content area is roughly
  // 5.5" tall after the header, so size by height not width to avoid
  // overflowing the bottom edge.
  const archPath = path.join(__dirname, "..", "docs", "ros_architecture.png");
  // Original aspect roughly 18 x 12 → 1.5.
  const h = 5.3, w = h * (18 / 12);
  const x = (W - w) / 2;
  s.addImage({ path: archPath, x, y: 1.7, w, h });

  slides.push(s);
}

// ------ Slide 5: Operational flowchart ---------------------------------
{
  const s = lightSlide();
  slideHeader(s, "03 · Operational Flow",
              "Deterministic state machine - one branch per FSM state");

  const fcPath = path.join(__dirname, "..", "docs", "operational_flowchart.png");
  // Flowchart is portrait-tall, so size by height.
  const h = 5.5, w = h * (11 / 16);
  s.addImage({ path: fcPath, x: 1.4, y: 1.6, w, h });

  // Text column on right.
  s.addText("Highlights", {
    x: 7.0, y: 1.7, w: 5.6, h: 0.4,
    fontSize: 18, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
  });
  s.addText([
    { text: "Voice or CLI command kicks off a mission",
      options: { bullet: true, breakLine: true } },
    { text: "Camera + LiDAR check independently for safety",
      options: { bullet: true, breakLine: true } },
    { text: "Pedestrians trigger a soft stop; objects trigger hard brake",
      options: { bullet: true, breakLine: true } },
    { text: "Mission ends with delivery box open then return home",
      options: { bullet: true } },
  ], {
    x: 7.0, y: 2.2, w: 5.6, h: 4.0,
    fontSize: 15, color: "262626", fontFace: "Calibri",
    paraSpaceAfter: 6,
  });

  slides.push(s);
}

// ------ Slide 6: Member overview ---------------------------------------
{
  const s = lightSlide();
  slideHeader(s, "04 · Member Contributions",
              "Every member owns at least 2 ROS functions");

  const members = [
    ["M1", "Vision Perception",      "camera_publisher · vision_detector"],
    ["M2", "LiDAR & Safety",         "lidar_obstacle · auto_brake (service)"],
    ["M3", "Localization & TF",      "gps_simulator · map_tf_broadcaster"],
    ["M4", "Navigation",             "waypoint_action_server · plan_helper"],
    ["M5", "Voice & Remote",         "voice_command · remote_telemetry"],
    ["M6", "Mission Control",        "mission_fsm · delivery_box_service"],
    ["M7", "CLI, Tests, Infra",      "click CLI · pytest · bringup launch"],
  ];

  // 7 cards, 4 per row first row, 3 second row.
  const cardW = 2.95, cardH = 2.2;
  members.forEach((m, i) => {
    const isTopRow = i < 4;
    const inRow = isTopRow ? 4 : 3;
    const idxInRow = isTopRow ? i : i - 4;
    const rowY = isTopRow ? 1.7 : 4.2;
    const totalRowWidth = inRow * cardW + (inRow - 1) * 0.2;
    const startX = (W - totalRowWidth) / 2;
    const x = startX + idxInRow * (cardW + 0.2);

    // Card body
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: rowY, w: cardW, h: cardH,
      fill: { color: WHITE }, line: { color: "DDDDDD", width: 0.75 },
      shadow: { type: "outer", color: "000000", blur: 4, offset: 1,
                angle: 135, opacity: 0.08 },
    });
    // Left accent bar in the member colour
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: rowY, w: 0.1, h: cardH,
      fill: { color: MEMBER_COLORS[m[0]] }, line: { type: "none" },
    });
    // Member ID
    s.addText(m[0], {
      x: x + 0.25, y: rowY + 0.15, w: 1.0, h: 0.45,
      fontSize: 22, bold: true, color: MEMBER_COLORS[m[0]],
      fontFace: "Calibri", margin: 0,
    });
    // Area name
    s.addText(m[1], {
      x: x + 0.25, y: rowY + 0.7, w: cardW - 0.35, h: 0.5,
      fontSize: 14, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
    });
    // Nodes
    s.addText(m[2], {
      x: x + 0.25, y: rowY + 1.25, w: cardW - 0.35, h: cardH - 1.4,
      fontSize: 10, color: "555555", fontFace: "Calibri", margin: 0,
    });
  });

  slides.push(s);
}

// ------ Slides 7..13: One slide per member -----------------------------
const memberDetail = [
  {
    id: "M1", area: "Vision Perception",
    package: "delivery_perception_vision",
    nodes: [
      ["camera_publisher_node", "Publisher",
       "Throttled republisher with resize + JPEG compression for the remote monitoring app."],
      ["vision_detector_node", "Subscriber + Custom-msg Publisher",
       "OpenCV HOG pedestrian detector + contour fallback. Emits ObstacleInfo messages."],
    ],
    primitives: ["Publisher", "Subscriber", "Custom Message"],
  },
  {
    id: "M2", area: "LiDAR & Safety",
    package: "delivery_perception_lidar",
    nodes: [
      ["lidar_obstacle_node", "Subscriber + Publisher",
       "Distills /scan into a single closest-forward ObstacleInfo for everyone else."],
      ["auto_brake_node", "Service Server",
       "Advertises EmergencyStop service; halts the robot when an obstacle crosses threshold."],
    ],
    primitives: ["Service Server", "Publisher", "Subscriber"],
  },
  {
    id: "M3", area: "Localization & TF",
    package: "delivery_localization",
    nodes: [
      ["gps_simulator_node", "Publisher",
       "Synthesises NavSatFix from /odom with Gaussian noise. Looks realistic in rosbag."],
      ["map_tf_broadcaster_node", "tf2 Broadcaster + Subscriber",
       "Keeps /map -> /odom alive; re-seeded by RViz 2D Pose Estimate."],
    ],
    primitives: ["tf2", "Publisher", "Subscriber"],
  },
  {
    id: "M4", area: "Navigation & Planning",
    package: "delivery_navigation",
    nodes: [
      ["waypoint_action_server_node", "Action Server",
       "DeliveryMission action wrapping move_base. Streams distance-remaining feedback."],
      ["global_planner_helper_node", "Subscriber + Publisher",
       "Compresses move_base global plans into a lean JSON summary."],
    ],
    primitives: ["Action Server", "Action Client", "Parameter Server"],
  },
  {
    id: "M5", area: "Voice & Remote Interface",
    package: "delivery_voice_remote",
    nodes: [
      ["voice_command_node", "Publisher + grammar",
       "Mic or text input -> VoiceCommand. Regex grammar maps natural language to commands."],
      ["remote_telemetry_node", "Multi-Subscriber + Publisher",
       "Aggregates 4 topics into a single JSON telemetry topic for the dashboard."],
    ],
    primitives: ["Custom Message", "Publisher", "Multi-Subscriber"],
  },
  {
    id: "M6", area: "Mission Control & Delivery",
    package: "delivery_mission",
    nodes: [
      ["delivery_box_service_node", "Service Server",
       "OpenDeliveryBox service with simulated actuator delay. Latched state topic."],
      ["mission_fsm_node", "Action Client + State Machine",
       "Brain of the robot. Drives FSM: voice -> deliver -> arrive -> box -> return home."],
    ],
    primitives: ["Service Server", "Action Client", "FSM"],
  },
  {
    id: "M7", area: "CLI, Tests, Infrastructure",
    package: "delivery_cli · delivery_tests · delivery_robot_bringup",
    nodes: [
      ["delivery-cli (click)", "Advanced CLI",
       "deliver, stop, resume, box, say, status, watch, bag, list-destinations subcommands."],
      ["delivery_tests + bringup", "pytest + roslaunch",
       "4 pytest modules, top-level launch, rosbag launch, parameter server config."],
    ],
    primitives: ["Click CLI", "pytest", "roslaunch", "rosbag"],
  },
];

memberDetail.forEach(m => {
  const s = lightSlide();
  slideHeader(s, `${m.id} · ${m.area}`, `Package: ${m.package}`);

  // Coloured left bar (motif continued from overview).
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 1.6, w: 0.25, h: H - 1.6,
    fill: { color: MEMBER_COLORS[m.id] }, line: { type: "none" },
  });

  // Two node cards.
  m.nodes.forEach((node, i) => {
    const y = 1.8 + i * 2.3;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y, w: 8.4, h: 2.0,
      fill: { color: "F7F8FC" }, line: { color: "E1E5EE", width: 0.75 },
    });
    // Node name
    s.addText(node[0], {
      x: 0.9, y: y + 0.15, w: 6.5, h: 0.45,
      fontSize: 18, bold: true, color: NAVY, fontFace: "Consolas", margin: 0,
    });
    // Primitive tag
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.9, y: y + 0.7, w: 2.7, h: 0.35,
      fill: { color: MEMBER_COLORS[m.id] }, line: { type: "none" },
    });
    s.addText(node[1], {
      x: 0.9, y: y + 0.7, w: 2.7, h: 0.35,
      fontSize: 11, bold: true, color: WHITE,
      align: "center", valign: "middle", fontFace: "Calibri", margin: 0,
    });
    // Description
    s.addText(node[2], {
      x: 0.9, y: y + 1.15, w: 8.0, h: 0.75,
      fontSize: 13, color: "262626", fontFace: "Calibri", margin: 0,
    });
  });

  // Right column: ROS primitives covered.
  s.addText("ROS Concepts", {
    x: 9.6, y: 1.85, w: 3.2, h: 0.4,
    fontSize: 14, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
  });
  m.primitives.forEach((p, i) => {
    const py = 2.35 + i * 0.55;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 9.6, y: py, w: 3.2, h: 0.45,
      fill: { color: WHITE },
      line: { color: MEMBER_COLORS[m.id], width: 1.5 },
    });
    s.addText(p, {
      x: 9.6, y: py, w: 3.2, h: 0.45,
      fontSize: 12, color: NAVY,
      align: "center", valign: "middle", fontFace: "Calibri", margin: 0,
    });
  });

  slides.push(s);
});

// ------ Slide: ROS functions coverage table ----------------------------
{
  const s = lightSlide();
  slideHeader(s, "05 · ROS Functions Coverage",
              "Every concept in the project brief is exercised somewhere");

  const rows = [
    ["ROS Concept",          "Where it lives"],
    ["Publisher",            "camera_publisher, gps_simulator, lidar_obstacle, telemetry, ..."],
    ["Subscriber",           "vision_detector, auto_brake, mission_fsm, remote_telemetry"],
    ["Custom Messages",      "ObstacleInfo, RobotStatus, VoiceCommand"],
    ["Service (server)",     "auto_brake (EmergencyStop), delivery_box (OpenDeliveryBox)"],
    ["Service (client)",     "mission_fsm, delivery-cli box / stop / resume"],
    ["Action (server)",      "waypoint_action_server (DeliveryMission)"],
    ["Action (client)",      "mission_fsm, delivery-cli deliver"],
    ["Parameter Server",     "move_base_overrides.yaml, waypoints.yaml"],
    ["tf2",                  "map_tf_broadcaster, navigation distance calc"],
    ["rosbag (mandatory)",   "record_session.launch, delivery-cli bag"],
    ["RViz",                 "delivery_robot.rviz with map, plan, scan, image"],
    ["roslaunch",            "10 launch files including delivery_robot_full.launch"],
    ["Click CLI (mandatory)","delivery_cli package with 9 subcommands"],
    ["Pytest (mandatory)",   "4 test modules: voice parser, CLI, box, LiDAR"],
  ];

  const tableRows = rows.map((r, i) => {
    if (i === 0) {
      return r.map(c => ({
        text: c,
        options: { bold: true, color: WHITE,
                   fill: { color: NAVY }, align: "left", fontSize: 13 }
      }));
    }
    const fill = (i % 2 === 0) ? "F7F8FC" : "FFFFFF";
    return r.map((c, j) => ({
      text: c,
      options: { color: "262626", fill: { color: fill },
                 fontSize: 12, bold: j === 0 }
    }));
  });

  s.addTable(tableRows, {
    x: 0.6, y: 1.7, w: 12.1,
    colW: [3.6, 8.5],
    rowH: 0.36,
    fontFace: "Calibri",
    border: { type: "solid", pt: 0.5, color: "E1E5EE" },
  });

  slides.push(s);
}

// ------ Slide: Demo + Recording -----------------------------------------
{
  const s = lightSlide();
  slideHeader(s, "06 · Demo & Recording",
              "What you will see in the 25-minute demonstration video");

  // Timeline of 5 steps along the top.
  const steps = [
    ["1", "Launch System",   "roslaunch delivery_robot_full"],
    ["2", "Start Recording", "delivery-cli bag start"],
    ["3", "Dispatch Mission","delivery-cli deliver library"],
    ["4", "Watch Telemetry", "delivery-cli watch"],
    ["5", "Replay rosbag",   "rosbag play demo.bag"],
  ];
  const stepW = 2.3;
  steps.forEach((st, i) => {
    const x = 0.7 + i * (stepW + 0.15);
    s.addShape(pres.shapes.OVAL, {
      x: x + (stepW - 0.7) / 2, y: 1.9, w: 0.7, h: 0.7,
      fill: { color: NAVY }, line: { type: "none" },
    });
    s.addText(st[0], {
      x: x + (stepW - 0.7) / 2, y: 1.9, w: 0.7, h: 0.7,
      fontSize: 18, bold: true, color: WHITE,
      align: "center", valign: "middle", fontFace: "Calibri", margin: 0,
    });
    s.addText(st[1], {
      x, y: 2.75, w: stepW, h: 0.4,
      fontSize: 13, bold: true, color: NAVY,
      align: "center", fontFace: "Calibri", margin: 0,
    });
    s.addText(st[2], {
      x, y: 3.15, w: stepW, h: 0.5,
      fontSize: 10, color: "555555",
      align: "center", fontFace: "Consolas", margin: 0,
    });
    if (i < steps.length - 1) {
      s.addShape(pres.shapes.LINE, {
        x: x + stepW - 0.05, y: 2.25, w: 0.25, h: 0,
        line: { color: ACCENT, width: 2 },
      });
    }
  });

  // What rosbag captures - 2 col grid below the timeline.
  s.addText("Rosbag Capture Topic Set", {
    x: 0.7, y: 4.1, w: W - 1.4, h: 0.4,
    fontSize: 18, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
  });
  const captureLeft = [
    "/cmd_vel       (control output)",
    "/scan          (LiDAR)",
    "/odom          (wheel odometry)",
    "/tf, /tf_static",
    "/camera/.../compressed",
  ];
  const captureRight = [
    "/delivery/status",
    "/delivery/gps/fix",
    "/delivery/perception/* (vision + LiDAR)",
    "/delivery/voice/commands",
    "/move_base/NavfnROS/plan",
  ];
  s.addText(captureLeft.map((t, i) => ({
    text: t, options: { bullet: true, breakLine: i < captureLeft.length - 1 }
  })), {
    x: 0.9, y: 4.7, w: 5.8, h: 2.5,
    fontSize: 13, color: "262626", fontFace: "Consolas",
  });
  s.addText(captureRight.map((t, i) => ({
    text: t, options: { bullet: true, breakLine: i < captureRight.length - 1 }
  })), {
    x: 6.9, y: 4.7, w: 5.8, h: 2.5,
    fontSize: 13, color: "262626", fontFace: "Consolas",
  });

  slides.push(s);
}

// ------ Slide: Testing strategy -----------------------------------------
{
  const s = lightSlide();
  slideHeader(s, "07 · Testing Strategy",
              "Pytest scenarios for fast iteration; rostest for integration");

  // Two big columns: unit vs integration.
  const colW = 5.9;
  const colY = 1.8;
  const colH = 4.8;

  // Left: Unit
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: colY, w: colW, h: colH,
    fill: { color: "F7F8FC" }, line: { color: "E1E5EE", width: 0.75 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: colY, w: colW, h: 0.08,
    fill: { color: MEMBER_COLORS.M1 }, line: { type: "none" },
  });
  s.addText("Unit Tests", {
    x: 0.85, y: colY + 0.25, w: colW - 0.5, h: 0.5,
    fontSize: 22, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
  });
  s.addText("pytest · no ROS master needed · seconds to run", {
    x: 0.85, y: colY + 0.8, w: colW - 0.5, h: 0.4,
    fontSize: 12, italic: true, color: MUTED, fontFace: "Calibri", margin: 0,
  });
  s.addText([
    { text: "test_voice_parser.py — 11 assertions on the grammar",
      options: { bullet: true, breakLine: true } },
    { text: "test_cli.py — Click CliRunner exercises --help / --version, bag list",
      options: { bullet: true, breakLine: true } },
    { text: "Stubs out rospy + delivery_msgs so it runs in a plain virtualenv",
      options: { bullet: true } },
  ], {
    x: 0.85, y: colY + 1.5, w: colW - 0.5, h: colH - 1.8,
    fontSize: 14, color: "262626", fontFace: "Calibri",
    paraSpaceAfter: 6,
  });

  // Right: Integration
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.8, y: colY, w: colW, h: colH,
    fill: { color: "F7F8FC" }, line: { color: "E1E5EE", width: 0.75 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.8, y: colY, w: colW, h: 0.08,
    fill: { color: MEMBER_COLORS.M4 }, line: { type: "none" },
  });
  s.addText("Integration Tests", {
    x: 7.05, y: colY + 0.25, w: colW - 0.5, h: 0.5,
    fontSize: 22, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
  });
  s.addText("rostest · roslaunch starts the node, pytest hits it", {
    x: 7.05, y: colY + 0.8, w: colW - 0.5, h: 0.4,
    fontSize: 12, italic: true, color: MUTED, fontFace: "Calibri", margin: 0,
  });
  s.addText([
    { text: "test_delivery_box_service.test — service round-trip + idempotency",
      options: { bullet: true, breakLine: true } },
    { text: "test_lidar_obstacle.py — synthetic /scan with known closest point",
      options: { bullet: true, breakLine: true } },
    { text: "--with-ros flag lets the same file run as plain pytest when desired",
      options: { bullet: true } },
  ], {
    x: 7.05, y: colY + 1.5, w: colW - 0.5, h: colH - 1.8,
    fontSize: 14, color: "262626", fontFace: "Calibri",
    paraSpaceAfter: 6,
  });

  slides.push(s);
}

// ------ Slide: Q&A / Thank you -----------------------------------------
{
  const s = darkSlide();
  // Big accent shape
  s.addShape(pres.shapes.RECTANGLE, {
    x: W - 5, y: -1, w: 6, h: 6,
    fill: { color: ACCENT, transparency: 80 }, line: { type: "none" },
    rotate: 20,
  });

  s.addText("Thank you", {
    x: 1.0, y: 2.4, w: 11, h: 1.2,
    fontSize: 64, bold: true, color: WHITE, fontFace: "Calibri", margin: 0,
  });
  s.addText("Questions?", {
    x: 1.0, y: 3.7, w: 11, h: 0.7,
    fontSize: 28, italic: true, color: ICE, fontFace: "Calibri", margin: 0,
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 1.05, y: 4.55, w: 0.6, h: 0.05, fill: { color: ACCENT },
    line: { type: "none" },
  });
  s.addText("github.com/<your-team>/campus_delivery_robot", {
    x: 1.0, y: 4.75, w: 11, h: 0.4,
    fontSize: 14, color: ICE, fontFace: "Consolas", margin: 0,
  });

  slides.push(s);
}

// Stamp page numbers (skip title + Q&A).
slides.forEach((s, i) => {
  if (i === 0 || i === slides.length - 1) return;
  pageNumber(s, i + 1, slides.length);
});

const outPath = path.join(__dirname, "..", "docs", "Campus_Delivery_Robot.pptx");
pres.writeFile({ fileName: outPath }).then(() => {
  console.log("wrote", outPath);
});
