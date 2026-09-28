# Physical AI & Robotics: Technical Implementation & Operational Logs

This repository contains engineering implementation records, kinematic control algorithms, simulation environments, and reinforcement learning pipelines developed and verified on local GPU workstation hardware.

---

## 1. System & Hardware Specifications

All implementations and simulation benchmarks were executed on the following local engineering stack:

| Component | Technical Specification | Operational Notes |
| :--- | :--- | :--- |
| **GPU** | **NVIDIA GeForce RTX 5060 Ti (16GB VRAM)** | Provides ample memory bandwidth for high-concurrency multi-agent simulation (`num_envs: 2048–4096`) |
| **Host OS** | **Ubuntu 22.04.5 LTS** (x86_64, Kernel 6.8) | Standard LTS distribution for modern robotics and AI frameworks |
| **NVIDIA Driver** | **580 Series (580.178.04)** | Native support for Ada Lovelace / Blackwell architectures & CUDA 12.8 |
| **Robotics Middleware** | **ROS 2 Humble Hawksbill Desktop** | Standard inter-process communication, topics, nodes, and TF2 transforms |
| **Simulation Platforms** | **Gazebo Classic**, **NVIDIA Isaac Sim 5.1.0**, **MuJoCo 3.x** | Multi-tiered physics engines for mobile, manipulator, and humanoid platforms |
| **RL Framework** | **Isaac Lab v2.3.2** (`rsl_rl`) | High-throughput GPU-accelerated reinforcement learning stack |
| **Robotic Platforms** | **Turtlebot3 (`waffle_pi`)**, **ReactorX 150**, **Unitree G1 (29-DoF)** | Mobile base, 5-DoF serial arm, and 29-DoF full-body humanoid robot |

---

## 2. Directory Structure & Module Index

```
PhysicalAiLab/
├── 01_sim_environment_setup/       # ROS 2 & Gazebo environment configuration
│   └── simulation_environment_setup.md
├── 02_open_loop_control/           # Turtlebot3 open-loop kinematics & trajectory tracking
│   ├── open_loop.py
│   ├── open_loop_trajectory_control.md
│   └── turtlebot3_waypoint[1-4]_*.png
├── 03_closed_loop_control/         # Turtlebot3 closed-loop odometry feedback & PD control
│   ├── closed_loop.py
│   ├── visualization.py
│   └── closed_loop_trajectory_control.md
└── 04_unitree_g1_rl_sim2sim/       # Unitree G1 humanoid RL & MuJoCo Sim2Sim pipeline
    ├── unitree_g1_rl_sim2sim_log_en.md (English Implementation Log)
    ├── unitree_g1_rl_sim2sim_log.md (Japanese Implementation Log)
    └── imgs/                       # 12 real-time verification screenshots
```

---

## 3. Module Summaries

### [01_sim_environment_setup](file:///root/bra/PhysicalAiLab/01_sim_environment_setup/simulation_environment_setup.md)
- **Scope:** Base robotics simulation infrastructure.
- **Key Deliverables:**
  - Automated deployment of ROS 2 Humble Desktop and colcon build tools.
  - Integration of Turtlebot3 (`waffle_pi`) differential-drive platform within Gazebo.
  - Integration of Interbotix ReactorX 150 (5-DoF) robotic arm and Joint State Publisher GUI verification.

### [02_open_loop_control](file:///root/bra/PhysicalAiLab/02_open_loop_control/open_loop_trajectory_control.md)
- **Scope:** Open-loop dead-reckoning trajectory control.
- **Key Deliverables:**
  - Planar differential-drive kinematics modeling ($P_W$ and rotation matrix $R_{WR}$ around $Z$-axis).
  - 10 Hz non-blocking state machine navigation through a $16\,\text{m}$ square circuit (`[4,0] -> [4,4] -> [0,4] -> [0,0]`).
  - Empirical parameter tuning compensating for ODE physics engine contact damping, achieving $< 0.35\,\text{m}$ terminal drift error.
  - Real-time simulation screenshots embedded for all 4 waypoint transitions.

### [03_closed_loop_control](file:///root/bra/PhysicalAiLab/03_closed_loop_control/closed_loop_trajectory_control.md)
- **Scope:** Sensor-feedback closed-loop navigation.
- **Key Deliverables:**
  - Real-time wheel odometry subscription (`/odom`) and quaternion-to-Euler yaw extraction.
  - Angular wraparound error correction restricted strictly to $[-\pi, \pi]$.
  - Proportional-Derivative (PD) heading controller with trajectory export to CSV and 2D visual trajectory plotting.

### [04_unitree_g1_rl_sim2sim](file:///root/bra/PhysicalAiLab/04_unitree_g1_rl_sim2sim/unitree_g1_rl_sim2sim_log_en.md)
- **Scope:** Unitree G1 humanoid reinforcement learning and Sim2Sim deployment.
- **Key Deliverables:**
  - Stable integration of NVIDIA Isaac Sim 5.1.0 with Isaac Lab v2.3.2 on RTX 5060 Ti 16GB.
  - Parallelized velocity-tracking training (`rsl_rl`) for the 29-DoF Unitree G1 humanoid model.
  - Real-time TensorBoard training telemetry monitoring (curriculum levels, reward terms, contact stability).
  - Cross-simulator transfer (Sim2Sim) into the MuJoCo physics engine via Unitree SDK2 and a standalone C++ controller (`g1_ctrl`), enabling real-time locomotion driven by virtual gamepad inputs.
  - Complete bilingual documentation available in both [English](file:///root/bra/PhysicalAiLab/04_unitree_g1_rl_sim2sim/unitree_g1_rl_sim2sim_log_en.md) and [Japanese](file:///root/bra/PhysicalAiLab/04_unitree_g1_rl_sim2sim/unitree_g1_rl_sim2sim_log.md).

---

## 4. Verification & Operational Authenticity

All code, models, configuration files, and visual media across this repository reflect actual, hands-on engineering execution conducted directly on the target hardware. All screenshots were captured in real time during live simulation and training runs.
