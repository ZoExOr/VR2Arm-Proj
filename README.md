# VR2Arm: VR Teleoperation for Real-Robot Manipulation

## Overview

Collecting high-quality demonstrations is essential for imitation learning and teleoperation research. However, widely used interfaces like the SpaceMouse and keyboard often feel unnatural and restrict users to discrete, segmented motions. These limitations make it difficult to collect demonstrations for dynamic tasks that require reactive, continuous control on real robots.

To bridge the gap, we present VR2ARM, a VR-based teleoperation interface for natural hand-to-robot control and supporting demonstration collection, especially for dynamic tasks.

VR2Arm provides a VR-based teleoperation pipeline that enables natural hand-to-robot control on a real Franka Emika Panda robot. The system streams the VR controller’s pose in real time, and converts it into incremental end-effector commands for the robot. As the user moves their controller, the system computes small pose deltas and sends them to the Franka through an impedance controller, producing smooth and responsive arm motion. Button inputs are used for gripper open/close and calibration, allowing the user to quickly reset alignment between the virtual and physical robot.


<img width="1587" height="595" alt="vr_workflow" src="https://github.com/user-attachments/assets/8f7d3d5f-ab3b-4c12-b43c-5ca4ca46c583" />

## File Structure
```
VR2Arm-Proj/
├── scripts/
│   ├── env_wrappers.py   # LIBERO Environment wrappers
│   ├── vr2franka.py      # Teleoperation script for Franka Panda
│   └── vr2libero.py      # We include a teleoperation script for simulation (LIBERO), as we first validated the pipeline in simulation before deploying it on the real Franka robot
├── APK/
│   ├── teleop-debug.apk   # customized build of oculus_reader for teleoperation
├── README.md             # Project documentation
└── requirements.txt      # Python dependencies
```

## Setup the project
> Note: This setup has been tested in the Social AI Lab environment. Minor adjustments may be required depending on local system configurations.

### Hardware and System Requirements
- **Oculus Quest 3 controllers** (currently supports right-hand controller only)  
- **Ubuntu 20.04** (other platforms not yet tested)  
- **Python 3.8** recommended  

### 1. Clone the repository
```bash
git clone https://github.com/ZoExOr/VR2Arm-Proj.git
cd VR2Arm-Proj
```

### 2. (Optional) Create and activate a conda environment
```bash
conda create -n vr2arm python=3.8
conda activate vr2arm
```
> Note: This step is optional. The project is developed under **Python 3.8**, so using a dedicated conda environment is recommended for consistency.

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Oculus Reader

Setup instructions: https://github.com/rail-berkeley/oculus_reader

### 6. Install panda-py

Setup instructions: https://github.com/JeanElsner/panda-py
> Note: For compatibility with `libfranka`, it is recommended to download `panda_py_0.7.5_libfranka_0.10.0.zip` from [its release page](https://github.com/JeanElsner/panda-py/releases) .
> After downloading and extracting, install the wheel with:
```
pip install panda_python-0.7.5+libfranka.0.10.0-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
```

## How to install our customized version of `oculus_reader`
1. Put `teleop-debug.apk` in `oculus_reader/oculus_reader/APK`, replacing the original APK.
2. Reinstall APK with `python oculus_reader/install.py --reinstall`
> Note: The FPS should be 90 if installed correctly.

## Usage

1. Make sure all dependencies are installed.
2. Make sure the customized version of `oculus_reader` is installed.
3. Connect your Oculus Quest 3 to the laptop via cable.   
5. For **Franka teleoperation**: place the Quest 3 to the **left** of the laptop, with its cameras facing sideways.
6. Ensure the headset cameras have an unobstructed view of your controller during teleoperation. **Do not block the cameras**, for example by moving the controller under the desk.

   
**Illustration of teleoperation setup**  
   <img width="693" height="186" alt="VR Setup" src="https://github.com/user-attachments/assets/96a89b1a-8c2c-4ff3-a49b-b975b8892b50" />

6. Run the corresponding script for teleoperation.

