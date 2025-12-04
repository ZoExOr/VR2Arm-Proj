import time
import numpy as np
import threading
import sys
import select
import termios
import tty

from scipy.spatial.transform import Rotation as R
import panda_py
from panda_py import controllers
from panda_py import libfranka
from oculus_reader.reader import OculusReader
from demo_saver import save_demo

oculus_reader = OculusReader()

BOUNDARY = {
    'x': (0.1, 1.4),
    'y': (-0.24, 0.35),
    'z': (-0.1, 0.7)
}

def get_transformation(Rm, P):
    T = np.eye(4)
    T[:3, :3] = Rm
    T[:3, 3] = P.reshape(3)
    return T
    
def get_hand_pose_and_buttons():
    euler_head2rbt = np.array([90, 0, 0])
    R_head2rbt = R.from_euler('xyz', euler_head2rbt, degrees=True).as_matrix()

    transforms, buttons = oculus_reader.get_transformations_and_buttons()
    T_hand2head = transforms['r'].copy()
    R_hand2head = T_hand2head[:3, :3]
    P_hand2head = T_hand2head[:3, 3].reshape(3, 1)
    P_head2rbt = np.zeros((3,1))
    T_head2rbt = get_transformation(R_head2rbt, P_head2rbt)
    T_hand2head[:3,:3] = R_hand2head
    T_hand2head[:3, 3] = P_hand2head.reshape(3)
    T_hand2rbt = T_head2rbt @ T_hand2head
    R_hand2rbt = T_hand2rbt[:3, :3]
    P_hand2rbt = T_hand2rbt[:3, 3].reshape(3, 1)

    return R_hand2rbt, P_hand2rbt, buttons

def wait_for_valid_pose(reader, timeout=3.0):
    start = time.time()
    while time.time() - start < timeout:
        transforms, buttons = reader.get_transformations_and_buttons()
        if transforms and 'r' in transforms:
            T = transforms['r']
            if not np.allclose(T, 0) and np.all(np.isfinite(T)):
                return transforms, buttons
        time.sleep(0.01)
    raise RuntimeError("No valid Oculus pose within timeout")

def exceed_boundary(pos):
    pos = pos.flatten()

    return not (BOUNDARY['x'][0] <= pos[0] <= BOUNDARY['x'][1] and
                BOUNDARY['y'][0] <= pos[1] <= BOUNDARY['y'][1] and
                BOUNDARY['z'][0] <= pos[2] <= BOUNDARY['z'][1])

def clamp_pos(x_d):
    x_d[0] = np.clip(x_d[0], BOUNDARY['x'][0], BOUNDARY['x'][1])
    x_d[1] = np.clip(x_d[1], BOUNDARY['y'][0], BOUNDARY['y'][1])
    x_d[2] = np.clip(x_d[2], BOUNDARY['z'][0], BOUNDARY['z'][1])
    
    return x_d

def get_key():
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1)
    return None

def grasp(gripper):
    is_grasping = False    
    prev_rg     = False     

    while True:
        _, _, buttons = get_hand_pose_and_buttons()
        if buttons is None:
            continue

        rg = buttons['RG']

        if rg and not prev_rg and not is_grasping:
            # print("button detected, closing…")
            try:
                ok = gripper.grasp(0.01, 0.05, 15, 20, 1)
                if ok:
                    is_grasping = True
                    # print("grasp success")
                else:
                    print("grasp failed")
            except RuntimeError as e:
                print("grasp error:", e)

        if (not rg) and prev_rg and is_grasping:
            # print("opening the gripper")
            try:
                gripper.move(0.08, 0.05)
            except RuntimeError as e:
                print("open error:", e)
            is_grasping = False

        prev_rg = rg       

def warm_up(move_thresh=0.05):
    """
    Wait until a significant movement of the controller is detected.
    The function continuously measures the controller's position and only returns 
    when the displacement exceeds the given threshold (in meters).
    """


    print("\033[1;33mInitializing... Please move the controller significantly until detection is confirmed.\033[0m")
    print("\033[1;32mHINT:\033[0m \033[1;33mtry moving the controller \033[1;32mFASTER and with sharper motions\033[1;33m so the system can detect it more reliably\033[0m\n")

    _, pos_prev, _ = get_hand_pose_and_buttons()
    while True:
        _, pos_cur, _ = get_hand_pose_and_buttons()
        delta = float(np.linalg.norm(pos_cur - pos_prev))  
        if delta > move_thresh:
            print("\033[1;33mController movement detected, starting teleoperation in 5s...\033[0m")
            print("\033[1;33mPlease move to a comfortable starting position.\033[0m\n")
            return

        pos_prev = pos_cur.copy()
        time.sleep(0.01) 


def run_teleop(duration=60, save_data=False, user_id="user1", task_id=1, demo_id=1, device_name="vr"):
    hostname = '172.16.0.2'
    panda = panda_py.Panda(hostname)
    gripper = libfranka.Gripper(hostname)
    panda.move_to_start()
    impedance = np.diag([600, 600, 600, 40, 40, 40])  
    # impedance = np.diag([60, 60, 60, 20, 20, 20])  

    ctrl = controllers.CartesianImpedance(
        impedance=impedance,
        damping_ratio=0.7,
        nullspace_stiffness=0.5,
        # filter_coeff=0.1
        filter_coeff=0.8
    )
    panda.get_robot().set_collision_behavior(
        [200.0, 200.0, 200.0, 200.0, 200.0, 200.0, 200.0],
        [200.0, 200.0, 200.0, 200.0, 200.0, 200.0, 200.0],
        [200.0, 200.0, 200.0, 200.0, 200.0, 200.0],
        [200.0, 200.0, 200.0, 200.0, 200.0, 200.0]
    )

    t_grasp = threading.Thread(target=grasp, args=(gripper,), daemon=True)
    t_grasp.start()

    rot_prev, pos_prev, buttons_prev = None, None, None
    t_wait_start = time.time()

    print("\033[1;33mSetting up oculus reader...\033[0m")
    oculus_reader.wait_until_ready(timeout_s=5.0)


    print("\033[1;33mPress any button to start...\033[0m\n")
    while True:
        rot_prev, pos_prev, buttons_prev = get_hand_pose_and_buttons()
        if buttons_prev is not None:
            if buttons_prev.get('RG', False) or buttons_prev.get('RTr', False) or buttons_prev.get('A', False) or buttons_prev.get('B', False):
                break
        if time.time() - t_wait_start > 10:
            t_wait_start = time.time()
        time.sleep(0.01)

    warm_up()
    time.sleep(5)

    print("\033[1;33m-------------------------- Teleoperation started --------------------------\033[0m\n")
    print("--------------------------\033[1;33m Press \033[1;32mmiddle finger\033[1;33m button to \033[1;32mgrasp/release\033[1;33m --------------------------\033[0m")
    print("--------------------------\033[1;33m Press \033[1;32mindex finger\033[1;33m button to \033[1;32mpause\033[1;33m teleop --------------------------\033[0m")
    # print("--------------------------\033[1;33m Press \033[1;32mA\033[1;33m button to \033[1;31mstop\033[1;33m teleop --------------------------\033[0m\n")

    rot_prev, pos_prev, buttons_prev = get_hand_pose_and_buttons()

    panda.start_controller(ctrl)
    
    x0 = panda.get_position().reshape(3, 1)
    R_hand_ref = R.from_matrix(rot_prev)
    q_robot_ref = panda.get_orientation().copy()   
    q_prev = q_robot_ref.copy()                 

    '''
    scale for fliping the object within a pan & paper drawing: 
        pos_scale = 2
        ori_scale = 1.5

    scale (possibly) for juggling the ball:
        pos_scale = 2.2
        ori_scale = 2
    '''

    pos_scale = 2
    ori_scale = 2

    start_time = time.time()
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())

    start_time = time.time()
    success_flag = 0
    task_duration = 0.0

    try:
        with panda.create_context(frequency=90) as ctx:
            while ctx.ok():
                elapsed = time.time() - start_time
                if elapsed > duration:
                    print("\033[1;31mTime limit reached.\033[0m")
                    break

                rot_curr, pos_curr, buttons_curr = get_hand_pose_and_buttons()
                if pos_curr is None or buttons_curr is None:
                    continue

                d_pos = pos_scale * (pos_curr - pos_prev)
                x_d = x0 + d_pos

                R_hand_curr = R.from_matrix(rot_curr)
                R_delta = R_hand_curr * R_hand_ref.inv()
                rotvec = R_delta.as_rotvec()     
                rotvec_scaled = ori_scale * rotvec
                R_scaled = R.from_rotvec(rotvec_scaled)
                R_target = R_scaled * R.from_quat(q_robot_ref)
                q_new = R_target.as_quat()

                if np.dot(q_new, q_prev) < 0:
                    q_new = -q_new  

                q_d = q_new

                if exceed_boundary(x_d):
                    clamp_pos(x_d)

                if buttons_curr['RTr']:
                    pos_prev = pos_curr
                    R_hand_ref = R.from_matrix(rot_curr)
                    q_robot_ref = q_prev.copy()
                    time.sleep(0.1)
                    continue

                # if buttons_curr['A']:
                #     success_flag = 1
                #     task_duration = round(elapsed, 2)
                #     print(f"\033[1;32mTask terminated by user\033[0m, duration:{task_duration}")
                #     break
                
                key = get_key()
                if key in ['y', 'Y']:
                    success_flag = 1
                    task_duration = round(elapsed, 2)
                    print("\033[33m[\033[1;32msuccess\033[33m] teleop terminated. time:\033[0m", task_duration)
                    break
                elif key in ['n', 'N']:
                    success_flag = 0
                    task_duration = round(elapsed, 2)
                    print("\033[33m[\033[1;31mfail\033[33m] teleop terminated time:\033[0m", task_duration)
                    break

                ctrl.set_control(x_d.reshape(3, 1), q_d)

                x0 = x_d.copy()
                q_prev = q_new           
                rot_prev, pos_prev, buttons_prev = rot_curr, pos_curr, buttons_curr

    except Exception as e:
        success_flag = 0
        task_duration = round(time.time() - start_time, 2)
        print("\033[1;31m[Emergency/Exception detected]\033[0m", task_duration)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

        if task_duration == 0.0:
            task_duration = round(time.time() - start_time, 2)

        if success_flag == 0:
            task_duration = round(time.time() - start_time, 2)

        if save_data:
            save_demo(user_id, task_id, demo_id, device_name, task_duration, success_flag)

        print("\033[1;32mTeleoperation finished.\033[0m. Task Duration: ", task_duration, "\n\n\n")
        time.sleep(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--save", type=str, default="false")
    parser.add_argument("--user", type=str, default="1")
    parser.add_argument("--task", type=int, default=0)
    parser.add_argument("--demo", type=int, default=1)
    args = parser.parse_args()

    run_teleop(
        duration=args.duration,
        save_data=(args.save.lower() == "true"),
        user_id=args.user,
        task_id=args.task,
        demo_id=args.demo,
        device_name="vr"
    )

    import os
    os._exit(0)
