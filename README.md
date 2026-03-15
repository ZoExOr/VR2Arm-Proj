# VR2Arm: VR Teleoperation for Real-Robot Manipulation


[Yijun Zhou](https://zoexor.github.io), [Muhan Hou](https://mh-hou.github.io), [Kim Baraka](https://www.kimbaraka.com/)

[Page](https://arxiv.org/abs/2601.13042)  | [Website](https://zoexor.github.io/vr2arm-page/)

## Overview

The project is developed at the **[Social AI Lab, Vrije Universiteit Amsterdam (VU)](https://www.socialai.nl/)**.

In this work, we introduce VR2Arm, a VR-controller-based teleoperation interface. By enabling an intuitive hand-to-robot control pipeline, VR2Arm allows users to collect high-quality demonstrations on a real Franka Emika Panda robot, with particular advantages in dynamic tasks that require reactive and continuous motion.
<img width="80%" height=auto alt="image" src="https://github.com/user-attachments/assets/8b16c0fe-a6ed-4456-b95a-7376b9b0ce9d" />

### How VR2ARM works
- Install the required dependencies (listed below)
- Place the headset in front of you
- Intuitive hand-to-robot control: move and rotate the controller to control the end-effector
- Front button for calibration; side button to grasp and release the gripper

### Key highlights
- Improved user task performance: higher success rates (especially on dynamic tasks), shorter successful execution times across tasks, and earlier successes across attempts

- Better user experience: significantly lower workload and higher usability
  
### To check our paper:
[Static Is Not Enough: A Comparative Study of VR and SpaceMouse in Static and Dynamic Teleoperation Tasks](https://arxiv.org/abs/2601.13042)

# Try it out!

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
> Note: Minor adjustments may be required depending on local system configurations.


## Hardware and System Requirements
- **Oculus Quest 3 controllers** (currently supports right-hand controller only)  
- **Ubuntu 20.04** (other platforms not yet tested)  
- **Python 3.8** recommended  

---

## Hardware Setup

### Franka Emika Research 3
For detailed instructions on initializing the robot arm, please refer to the documentation:
> [Getting Started with Franka Emika Research 3](https://socialrobotics.atlassian.net/wiki/spaces/CBSR/pages/2412675074/Getting+started+with+Franka+Emika+Research+3)

### Oculus Quest 3
1.  **Connection:** Connect the headset to your PC via USB and click **"USB detected"** inside the Quest 3.
2.  **Terminal Setup:** Follow the yellow highlighted instructions in your terminal.
3.  **Activation:** When the message `"setting up oculus reader..."` appears, put on the headset to activate the sensors and proceed.

---
## Dependencies Setup

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

### 4. Install [Modified Oculus Reader](https://github.com/ZoExOr/oculus_reader_modified) as dependency

```bash
pip install git+https://github.com/ZoExOr/oculus_reader_modified.git
```

### 5. Set up ADB


Before running the reader, ensure your hardware is configured correctly. Follow the official [ADB Setup Guide](https://github.com/rail-berkeley/oculus_reader?tab=readme-ov-file#setup-of-the-adb) from the original repository to enable communication with your headset.

To test:
```bash
# Ensure you are in the project root
python oculus_reader/reader.py
```
> Note: If the installation and ADB connection are successful, the frequency output should stabilize at 90 FPS.


### 6. Install panda-py

Setup instructions: https://github.com/JeanElsner/panda-py
> Note: For compatibility with `libfranka`, it is recommended to download `panda_py_0.7.5_libfranka_0.10.0.zip` from [its release page](https://github.com/JeanElsner/panda-py/releases) .
> After downloading and extracting, install the wheel with:
```
pip install panda_python-0.7.5+libfranka.0.10.0-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
```

## Usage

1. Make sure all dependencies are installed.
2. Make sure the customized version of `oculus_reader` is installed.
3. Connect your Oculus Quest 3 to the laptop via cable.   
5. For **Franka teleoperation**: place the Quest 3 to the **left** of the laptop, with its cameras facing sideways.
6. Ensure the headset cameras have an unobstructed view of your controller during teleoperation. **Do not block the cameras**, for example by moving the controller under the desk.

   
**Illustration of teleoperation setup**  
   <img width="693" height="186" alt="VR Setup" src="https://github.com/user-attachments/assets/96a89b1a-8c2c-4ff3-a49b-b975b8892b50" />

6. Run the corresponding script for teleoperation.

