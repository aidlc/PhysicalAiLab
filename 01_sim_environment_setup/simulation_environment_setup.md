# Technical Operation Record: ROS 2 & Gazebo Simulation Environment Setup

**Document Type:** Technical Implementation & Operational Record  
**Target Platforms:** Turtlebot3 Mobile Robot (`waffle_pi`), Interbotix ReactorX 150 Manipulator (`rx150`)  
**Core Frameworks:** Ubuntu 22.04 LTS, ROS 2 Humble Desktop, Gazebo Simulator (Classic)  

---

## 1. Overview & Objectives

This implementation log details the step-by-step technical procedures, environment configuration, and verification testing for establishing a robotics simulation pipeline. The objective is to deploy a standardized simulation platform incorporating both a differential-drive mobile robot (Turtlebot3) and a multi-axis robotic manipulator (Interbotix ReactorX 150) inside Gazebo for kinematic and control algorithm validation.

---

## 2. Infrastructure & Virtualization Setup

For simulation and robotics software development, Linux (Ubuntu 22.04 LTS) serves as the primary operating system environment. 

### Virtualization Architecture
- **Hypervisor:** VMware Workstation Pro (Windows hosts) / VMware Fusion Pro (macOS hosts) / Native Dual-Boot Linux.
- **VM Resource Allocation:**
  - **Storage:** Minimum 50 GB dynamically allocated virtual disk (stored as a single file).
  - **CPU / Memory:** Minimum 4 vCPUs, 8 GB+ RAM allocated for real-time 3D simulation rendering and ROS 2 middleware processing.
- **Hardware Architecture Note:** x86_64 (amd64) architecture is strictly recommended for full compatibility with binary libraries of third-party robot hardware SDKs (e.g., Interbotix Dynamixel drivers).

---

## 3. ROS 2 Humble Deployment

ROS 2 Humble Hawksbill is the targeted Long Term Support (LTS) middleware release for Ubuntu 22.04.

### Method 1: Official Debian Repository Installation

```bash
# Ensure standard Ubuntu universe repository is enabled
sudo apt update && sudo apt install -y software-properties-common curl gnupg lsb-release
sudo add-apt-repository universe

# Add ROS 2 GPG key
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# Add ROS 2 repository to apt sources
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS 2 Desktop (includes ROS, RViz, demos, and tutorials)
sudo apt update
sudo apt install -y ros-humble-desktop
```

### Method 2: Automated Deployment Script (Fast Network Mirror)

For network environments requiring accelerated local mirrors:

```bash
wget http://fishros.com/install -O fishros && . fishros
```

---

## 4. ROS 2 Workspace Configuration

### Build Tools & Base Dependencies

```bash
# Install colcon build system and git version control
sudo apt update
sudo apt install -y python3-colcon-common-extensions git python3-rosdep
```

### Initializing the Workspace (`ros2_ws`)

```bash
# Create workspace directory structure
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws

# Initialize compilation
colcon build

# Persist environment sourcing in shell initialization
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### Creating Project Package (`robotics101`)

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python robotics101

# Build package with symlink install for iterative Python development
cd ~/ros2_ws
colcon build --symlink-install
```

---

## 5. Gazebo Simulator & Turtlebot3 Stack Setup

### Installing Simulation & Navigation Dependencies

```bash
# Install Gazebo ROS packages
sudo apt install -y ros-humble-gazebo-*

# Install Cartographer SLAM packages (optional)
sudo apt install -y ros-humble-cartographer ros-humble-cartographer-ros

# Install Navigation2 stack (optional)
sudo apt install -y ros-humble-navigation2 ros-humble-nav2-bringup
```

### Building Turtlebot3 Packages in Dedicated Workspace

```bash
# Create workspace for Turtlebot3
mkdir -p ~/turtlebot3_ws/src
cd ~/turtlebot3_ws/src/

# Clone Turtlebot3 repositories (Humble branch)
git clone -b humble https://github.com/hanzheteng/turtlebot3
git clone -b humble https://github.com/hanzheteng/turtlebot3_msgs
git clone -b humble https://github.com/hanzheteng/turtlebot3_simulations
git clone -b humble https://github.com/hanzheteng/DynamixelSDK

# Build Turtlebot3 workspace
cd ~/turtlebot3_ws
colcon build --symlink-install

# Configure environment variables
echo "source ~/turtlebot3_ws/install/setup.bash" >> ~/.bashrc
echo "export TURTLEBOT3_MODEL=waffle_pi" >> ~/.bashrc
echo "source /usr/share/gazebo/setup.sh" >> ~/.bashrc
source ~/.bashrc
```

### Runtime Verification: Turtlebot3 in Gazebo

1. **Launch Simulation World:**
   ```bash
   ros2 launch turtlebot3_gazebo empty_world.launch.py
   ```
2. **Launch Teleoperation Node (in a separate terminal):**
   ```bash
   ros2 run turtlebot3_teleop teleop_keyboard
   ```
3. **Operational Notes:**
   - Keep the teleoperation terminal focused to publish velocity commands (`/cmd_vel`) via keyboard keys (`w/a/s/d/x`).
   - Clean termination: Always exit with `Ctrl + C` and allow Gazebo approximately 5–10 seconds to gracefully release shared memory and graphics sockets. Abrupt terminal termination without process cleanup can result in port locks and simulator launch crashes.

---

## 6. Robotic Manipulator Setup: Interbotix ReactorX 150

The ReactorX 150 (RX-150) is a 5-DoF robotic arm driven by Dynamixel D-Series servomotors.

### Installation via Automated Shell Script

```bash
# Official repository install
sudo apt install -y curl
curl 'https://raw.githubusercontent.com/Interbotix/interbotix_ros_manipulators/main/interbotix_ros_xsarms/install/amd64/xsarm_amd64_install.sh' > ~/xsarm_amd64_install.sh
chmod +x ~/xsarm_amd64_install.sh
~/xsarm_amd64_install.sh -d humble
```

*Installation Prompts:*
- Perception packages: Select `n` (not required for base kinematic simulation).
- MATLAB-ROS API: Select `n`.

### Persisting Manipulator Workspace

```bash
echo "source ~/interbotix_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### Verifying Installed Packages

```bash
ros2 pkg list | grep interbotix
```

Expected output includes:
```text
interbotix_common_modules
interbotix_common_sim
interbotix_common_toolbox
interbotix_ros_xsarms
interbotix_ros_xsarms_examples
interbotix_ros_xseries
interbotix_tf_tools
interbotix_xs_driver
interbotix_xs_modules
interbotix_xs_msgs
interbotix_xs_ros_control
interbotix_xs_rviz
interbotix_xs_sdk
interbotix_xs_toolbox
interbotix_xsarm_control
interbotix_xsarm_descriptions
interbotix_xsarm_dual
interbotix_xsarm_joy
interbotix_xsarm_moveit
interbotix_xsarm_moveit_interface
interbotix_xsarm_ros_control
interbotix_xsarm_sim
```

### Runtime Verification: Manipulator Joint State Publisher

Launch the RX-150 arm description with interactive Joint State Publisher GUI:

```bash
ros2 launch interbotix_xsarm_descriptions xsarm_description.launch.py robot_model:=rx150 use_joint_pub_gui:=true
```

- **GUI Operation:** Sliders allow direct manual actuation of individual joint angles in real time by publishing to `/joint_states`.
- **Randomize / Center:** Used for verification of joint limits, axis directions, and neutral homing positions.

---

## 7. Status & Summary

Both mobile robot (Turtlebot3 Waffle Pi) and serial manipulator (ReactorX 150) simulation environments have been successfully deployed and verified on Ubuntu 22.04 LTS with ROS 2 Humble. The development workspace is fully prepared for trajectory control and kinematics implementation.
