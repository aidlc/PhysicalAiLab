# Technical Implementation Record: Turtlebot3 Open-Loop Trajectory Control

**Document Type:** Technical Implementation & Verification Log  
**Platform:** Differential Drive Mobile Robot (Turtlebot3 `waffle_pi`)  
**Core Frameworks:** Ubuntu 22.04 LTS, ROS 2 Humble, Gazebo Classic  
**Source Implementation:** [`open_loop.py`](file:///root/bra/PhysicalAiLab/02_open_loop_control/open_loop.py)  

---

## 1. Objective & Technical Scope

This technical log records the design, implementation, and simulation validation of an open-loop kinematic control strategy for a differential-drive mobile robot. 

The control objective is to navigate the robot through a predetermined square trajectory defined by four Cartesian waypoints:
$$\text{Start } [0, 0] \longrightarrow \text{WP}_1 [4.0, 0.0] \longrightarrow \text{WP}_2 [4.0, 4.0] \longrightarrow \text{WP}_3 [0.0, 4.0] \longrightarrow \text{WP}_4 [0.0, 0.0]$$

Because open-loop control executes without closed-loop sensor feedback (i.e., pure dead-reckoning command dispatch), system accuracy depends entirely on precise kinematic modeling, calibration of wheel slippage, and runtime inertial compensation. The target threshold is to complete the entire 16-meter circuit with a terminal position error $< 1.0\,\text{m}$.

---

## 2. Kinematic Modeling & Frame Transformations

### 2.1 Differential Drive Kinematics
The mobile platform utilizes two coaxial drive wheels placed symmetrically around the chassis center with a passive caster for balance. The robot velocity is commanded via linear velocity $v$ and angular velocity $\omega$:

$$\begin{bmatrix} v \\ \omega \end{bmatrix} = \begin{bmatrix} \frac{r}{2} & \frac{r}{2} \\ \frac{r}{L} & -\frac{r}{L} \end{bmatrix} \begin{bmatrix} \omega_R \\ \omega_L \end{bmatrix}$$

where $r$ is the nominal wheel radius, $L$ is the track width (wheelbase separation), and $\omega_R, \omega_L$ denote the respective right and left wheel angular velocities.

### 2.2 Coordinate Frames & Rotational Transformation
- **Robot Body Frame $\{R\}$:** Centered midway between the driving wheels. The $X$-axis points forward along linear velocity $v$, the $Y$-axis points to the left, and the $Z$-axis points upwards.
- **World Coordinate Frame $\{W\}$:** Fixed ground reference frame aligned with the Gazebo origin $(0, 0, 0)$.

Under planar 2D assumptions, rotation between $\{R\}$ and $\{W\}$ is parameterized by planar yaw angle $\theta$ around the $Z$-axis. The position vector $P_W$ and rotation matrix $R_{WR}$ are:

$$P_W = \begin{bmatrix} x \\ y \\ 0 \end{bmatrix}$$

$$R_{WR} = \begin{bmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

### 2.3 Unit & Coordinate Conventions (REP 103)
The implementation strictly adheres to ROS Standard Units and Coordinate Conventions (REP 103):
- Position and distances: Meters ($\text{m}$)
- Linear velocities: Meters per second ($\text{m/s}$)
- Angles: Radians ($\text{rad}$)
- Angular velocities: Radians per second ($\text{rad/s}$)

---

## 3. Control Architecture & State Machine

The control logic in [`open_loop.py`](file:///root/bra/PhysicalAiLab/02_open_loop_control/open_loop.py) is architected as a non-blocking ROS 2 timer-driven state machine operating at a continuous publication frequency of **10 Hz** ($\Delta t = 0.1\,\text{s}$).

### Theoretical vs. Calibrated Parameters

To minimize wheel slip and acceleration jerk in simulation, moderate velocity profiles were selected:
- Linear speed $v = 0.2\,\text{m/s}$
- Angular speed $\omega = 0.2\,\text{rad/s}$

| Movement Segment | Theoretical Requirement | Theoretical Time | Theoretical Steps (10 Hz) | Calibrated Steps | Calibration Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Straight Leg** | $4.0\,\text{m}$ straight translation | $t = \frac{4.0}{0.2} = 20.0\,\text{s}$ | $200$ steps | **470 steps** | Compensates for Gazebo ODE physics damping, inertia, and non-ideal contact dynamics |
| **90° Turn** | $\frac{\pi}{2}\,\text{rad} \approx 1.5708\,\text{rad}$ in-place rotation | $t = \frac{\pi/2}{0.2} \approx 7.854\,\text{s}$ | $79$ steps | **152 steps** | Compensates for wheel lateral friction and angular acceleration ramp-up |

### State Transition Diagram

```
[FORWARD] (step < forward_count) ──> vel.linear.x = 0.2, vel.angular.z = 0.0
   │
   └── (step >= forward_count) ────> Transition to [TURN], reset step = 0
                                        │
[TURN] (step < turn_count) ───────────┘ ──> vel.linear.x = 0.0, vel.angular.z = 0.2
   │
   └── (step >= turn_count) ───────> side++, Transition to [FORWARD], reset step = 0
                                        │
                               (side >= 4) ──> [HALT] Cancel timer, publish zero vel
```

---

## 4. Hands-on Execution & Verification Records

The following screenshots record the actual verification results captured in real time from the Gazebo simulation runtime.

### Waypoint 1 Arrival: $[4.0, 0.0]$
The robot completes the first 4-meter translation along the $+X$ axis and executes an in-place 90° left rotation facing the $+Y$ axis.

![Waypoint 1 Arrival at (4, 0)](file:///root/bra/PhysicalAiLab/02_open_loop_control/turtlebot3_waypoint1_pos_4_0.png)

---

### Waypoint 2 Arrival: $[4.0, 4.0]$
The robot completes the second 4-meter translation along the $+Y$ axis and completes the second 90° rotation facing the $-X$ direction.

![Waypoint 2 Arrival at (4, 4)](file:///root/bra/PhysicalAiLab/02_open_loop_control/turtlebot3_waypoint2_pos_4_4.png)

---

### Waypoint 3 Arrival: $[0.0, 4.0]$
The robot translates 4 meters along the $-X$ direction to reach coordinate $[0.0, 4.0]$ and initiates its final 90° turn facing the $-Y$ direction.

![Waypoint 3 Arrival at (0, 4)](file:///root/bra/PhysicalAiLab/02_open_loop_control/turtlebot3_waypoint3_pos_0_4.png)

---

### Waypoint 4 / Origin Return: $[0.0, 0.0]$
The robot completes the fourth leg along the $-Y$ axis, returning to the origin area and automatically halting.

![Waypoint 4 Return to Origin (0, 0)](file:///root/bra/PhysicalAiLab/02_open_loop_control/turtlebot3_waypoint4_return_0_0.png)

### Quantitative Verification Summary
- **Target Circuit Distance:** $16.0\,\text{m}$ total path length.
- **Allowed Tolerance:** Within $1.0\,\text{m}$ of the origin $[0, 0]$.
- **Measured Terminal Position:** $(\Delta x \approx 0.18\,\text{m}, \Delta y \approx 0.25\,\text{m})$, yielding a terminal drift error of $\approx 0.31\,\text{m}$.
- **Result:** Successfully satisfies the design specification under open-loop conditions.

---

## 5. Execution Guide

```bash
# Terminal 1: Launch Gazebo with Turtlebot3 Waffle Pi model
ros2 launch turtlebot3_gazebo empty_world.launch.py

# Terminal 2: Execute trajectory controller
cd /root/bra/PhysicalAiLab/02_open_loop_control
python3 open_loop.py
```

*Operational Tip:* In the Gazebo viewport, pressing `Ctrl + R` resets the simulation model back to the origin $(0, 0, 0)$ without needing to restart the simulation process.
