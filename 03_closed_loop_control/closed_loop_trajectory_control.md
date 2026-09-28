# Technical Implementation Record: Turtlebot3 Closed-Loop Trajectory Control

**Document Type:** Technical Implementation & Verification Log  
**Platform:** Differential Drive Mobile Robot (Turtlebot3 `waffle_pi`)  
**Core Frameworks:** Ubuntu 22.04 LTS, ROS 2 Humble, Gazebo Classic, NumPy, Matplotlib  
**Source Implementations:** [`closed_loop.py`](file:///root/bra/PhysicalAiLab/03_closed_loop_control/closed_loop.py), [`visualization.py`](file:///root/bra/PhysicalAiLab/03_closed_loop_control/visualization.py)  

---

## 1. Objective & Technical Scope

While open-loop dead-reckoning demonstrates the kinematic foundations of differential drive robots, physical disturbances such as wheel slip, surface friction variations, and mechanical latency cause unbounded cumulative drift over extended operating periods.

This module implements a **closed-loop feedback controller** that continuously tracks the robot's pose from wheel odometry (`/odom`), dynamically corrects heading angle errors using a Proportional-Derivative (PD) controller, and logs trajectory coordinates to CSV for post-run analysis.

---

## 2. Controller Design & Kinematics

### 2.1 Odometry Feedback & Orientation Conversion
Odometry messages from `/odom` provide orientation in quaternion format $(q_x, q_y, q_z, q_w)$. The robot extracts the 2D planar heading angle (yaw $\theta$) using standard Euler angle conversion:

$$\theta = \text{atan2}\left(2(q_w q_z + q_x q_y),\, 1 - 2(q_y^2 + q_z^2)\right)$$

### 2.2 Heading Error Calculation with Wraparound
When steering toward a target waypoint $(x_{\text{target}}, y_{\text{target}})$, the desired heading angle is:

$$\theta_{\text{target}} = \text{atan2}(y_{\text{target}} - y_{\text{current}},\, x_{\text{target}} - x_{\text{current}})$$

Because angles are cyclic modulo $2\pi$, raw difference can cause false $360^\circ$ spins at the $(-\pi, \pi)$ boundary. Angular error is mapped strictly to $[-\pi, \pi]$:

$$e_\theta = \text{atan2}(\sin(\theta_{\text{target}} - \theta),\, \cos(\theta_{\text{target}} - \theta))$$

### 2.3 Proportional-Derivative (PD) Control Law
The angular velocity control command $\omega$ is computed via:

$$\omega = K_p \, e_\theta + K_d \, \frac{\Delta e_\theta}{\Delta t}$$

where $K_p = 1.0$ and $K_d = 0.1$ provide fast convergence with damped oscillation during heading realignment.

---

## 3. Implementation Files

- **[`closed_loop.py`](file:///root/bra/PhysicalAiLab/03_closed_loop_control/closed_loop.py):**
  - `Controller`: Generic PD controller with angular error normalization.
  - `Turtlebot`: ROS 2 Node managing odometry subscription, waypoint sequencing, velocity publication (`/cmd_vel`), and trajectory recording.
- **[`visualization.py`](file:///root/bra/PhysicalAiLab/03_closed_loop_control/visualization.py):**
  - Trajectory plotting utility utilizing Matplotlib to parse `trajectory.csv` and render actual 2D ground-truth motion paths.

---

## 4. Execution Workflow

```bash
# Terminal 1: Launch Gazebo Simulation
ros2 launch turtlebot3_gazebo empty_world.launch.py

# Terminal 2: Run Closed-Loop Navigation Node
cd /root/bra/PhysicalAiLab/03_closed_loop_control
python3 closed_loop.py

# Terminal 3: Plot and Inspect Trajectory Results
python3 visualization.py
```
