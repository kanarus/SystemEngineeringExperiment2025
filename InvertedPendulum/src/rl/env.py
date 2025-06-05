import numpy as np
from simulator.acrobot import swingup, balance, sys_iden
from collections import OrderedDict

def make_env(config):
    if config.domain == 'double_pendulum':
        if config.task == 'swingup':
            return SwingUp(config)
        elif config.task == 'balance':
            return Balance(config)
        elif config.task == 'sys_iden':
            return SysIden(config)
    else:
        raise NotImplementedError

class Balance():
    def __init__(self, config):
        self._config = config
        self._arrange = np.zeros(config.num_digitized_pendulum-1)
        self._env = balance()
        self._pendulum_limit = (-0.20*np.pi, 0.20*np.pi)
        self._arm_limit = (-0.9*np.pi, 0.9*np.pi)
        print('dt = ', config.repeat*self._env.control_timestep())
        self._digitized_action = np.linspace(self._env.action_spec().minimum[0], self._env.action_spec().maximum[0], config.num_action)
        print('alpha interval: ', np.linspace(self._pendulum_limit[0], self._pendulum_limit[1], config.num_digitized_pendulum+1)[1:-1])
        print('theta interval: ', np.linspace(self._arm_limit[0], self._arm_limit[1], config.num_digitized_arm +1)[1:-1])
        d_arm = config.num_digitized_arm
        d_pendulum = config.num_digitized_pendulum
        print('action interval: ', self._digitized_action)
        print('state-action is ', f"({d_arm}x{d_arm}x{d_pendulum}x{d_pendulum}) x {config.num_action}")
        print(f'total state-action number is {(d_arm**2)*((d_pendulum)**2)*config.num_action}')

    @property
    def action_space(self):
        return self._config.num_action

    @property
    def obs_space(self):
        return self._config.state_size
    
    def step(self, action, time=None, timedepedence=None):
        action = self._digitized_action[action]
        for _ in range(self._config.repeat):   
            obs = self._env.step(action).observation
        digitized_state, done, state_dict = self._digitized_state(obs)
        reward, best = self._get_reward(state_dict, done, action)
        state_dict["best"] = best
        return digitized_state, reward, done, state_dict

    def reset(self):
        obs = self._env.reset().observation
        digitized_state, _, state_dict = self._digitized_state(obs)
        return digitized_state

    def _get_reward(self, state_dict, done, action):
        if done:
            return -10, 0
        rew=0.1
        d_arm=self._config.num_digitized_arm
        d_pend = self._config.num_digitized_pendulum
        n_pendulum_rad,n_pendulum_vel=state_dict["n_pendulum_rad"],state_dict["n_pendulum_vel"]
        n_pend_best = (d_pend-1)/2
        n_arm_best = (d_arm-1)/2
        bonus=0
        n_arm_rad,n_arm_vel=state_dict["n_arm_rad"],state_dict["n_arm_vel"]
        if n_pendulum_rad == n_pend_best:
            bonus += 0.05

        # elif abs(n_pendulum_rad-n_pend_best) == 1:
        #     bonus += 0.05
        if n_arm_rad == n_arm_best:
            bonus += 0.05

        #if abs(n_pendulum_rad - n_pend_best) > 1:
        #   bonus -= 0.1

        #if abs(n_arm_rad - n_arm_best) > 1:
        #    bonus -= 0.1

        # elif abs(n_arm_rad-n_arm_best) == 1:
        #     bonus += 0.05
        return rew+bonus, 1 if bonus > 0 else 0
    
          

    def _digitized_state(self, obs):
        # 0 is positive z axis at doule pendulum pendulum angle 
        state_dict = OrderedDict()
        d_arm = self._config.num_digitized_arm
        d_pendulum = self._config.num_digitized_pendulum
        vec, vel = obs["orientations"], obs["velocity"]
        arm_vec, pendulum_vec = vec[0:2], vec[2:4]
        arm_vel, pendulum_vel = vel[0], vel[1]
        arm_rad = np.arctan2(arm_vec[1], arm_vec[0])
        pendulum_rad = np.arctan2(pendulum_vec[1], pendulum_vec[0])
        def make_length(left, right, cnt):
            if cnt == 0:
                return [right]
            mid = (left + right)/2
            right_list = make_length(mid, right, cnt - 1)
            res = [left] + right_list
            return res
        def make_div(lim0, lim1, div):
            tmp_left_list = make_length(lim0, 0.0, div//2)
            n_arm_rad = tmp_left_list.copy()
            tmp_left_list.pop()
            tmp_left_list.reverse()
            tmp_right_list = [-i for i in tmp_left_list]
            return n_arm_rad + tmp_right_list
        # arm_rad_div = make_div(self._arm_limit[0], self._arm_limit[1], d_arm)
        n_arm_rad = np.digitize(arm_rad, np.linspace(self._arm_limit[0], self._arm_limit[1], d_arm +1)[1:-1])
        # n_arm_rad = np.digitize(arm_rad, arm_rad_div[1:-1])
        n_arm_vel = np.digitize(arm_vel.clip(-8, 8), np.linspace(-8, 8, d_arm+1)[1:-1])

        # pendulum_rad_div = make_div(self._pendulum_limit[0], self._pendulum_limit[1], d_pendulum)
        n_pendulum_rad = np.digitize(pendulum_rad, np.linspace(self._pendulum_limit[0], self._pendulum_limit[1], d_pendulum+1)[1:-1] + self._arrange)
        # n_pendulum_rad = np.digitize(pendulum_rad, pendulum_rad_div[1:-1] + self._arrange)
        n_pendulum_vel = np.digitize(pendulum_vel.clip(-8, 8), np.linspace(-8, 8, d_pendulum+1)[1:-1])

        state_dict["arm_rad"] = arm_rad
        state_dict["pendulum_rad"] = pendulum_rad
        state_dict["arm_vel"] = arm_vel
        state_dict["pendulum_vel"] = pendulum_vel
        state_dict["n_arm_rad"] = n_arm_rad
        state_dict["n_pendulum_rad"] = n_pendulum_rad
        state_dict["n_arm_vel"] = n_arm_vel
        state_dict["n_pendulum_vel"] = n_pendulum_vel
        state_dict["digitized_state"] = n_pendulum_rad + n_pendulum_vel*d_pendulum + n_arm_vel*d_pendulum**2 + n_arm_rad*d_pendulum**2*d_arm

        arm_cond = n_arm_rad == 0 or n_arm_rad >= d_arm - 1
        pendulum_cond = n_pendulum_rad == 0 or n_pendulum_rad >= d_pendulum -1
        if arm_cond or pendulum_cond:
            done = True
        else:
            done = False
        return state_dict["digitized_state"], done, state_dict

class SwingUp():
    def __init__(self, config):
        self._config = config
        self._arrange = np.zeros(config.num_digitized-1)
        self._env = swingup()
        print('dt = ', self._env.control_timestep())
        # self._arrange[config.num_digitized//2] = -0.20
        # self._arrange[config.num_digitized//2 - 2] = 0.20
        self._digitized_action = np.linspace(self._env.action_spec().minimum[0], self._env.action_spec().maximum[0], config.num_action)
        print('alpha interval: ', np.linspace(-np.pi, np.pi, config.num_digitized+1)[1:-1] + self._arrange)
        print('theta interval: ', np.linspace(-np.pi, np.pi, config.num_digitized +1)[1:-1])
        d = config.num_digitized
        print('action interval: ', self._digitized_action)
        print('state-action is ', f"({d}x{d}x{d}x{d}) x {config.num_action}")
        print(f'total state-action number is {(d**2)*((d)**2)*config.num_action}')
    @property
    def action_space(self):
        return self._config.num_action
    @property
    def obs_space(self):
        return self._config.state_size
    
    def step(self, action, time=None, timedepedence=None):
        action = self._digitized_action[action]
        for _ in range(self._config.repeat):   
            obs = self._env.step(action).observation
        digitized_state, done, state_dict = self._digitized_state(obs)
        reward, best = self._get_reward(state_dict, done)
        state_dict["best"] = best
        return digitized_state, reward, done, state_dict

    def reset(self):
        obs = self._env.reset().observation
        digitized_state, _, state_dict = self._digitized_state(obs)
        return digitized_state

    def _get_reward(self, state_dict, done):
        pass

    def _digitized_state(self, obs):
        # 0 is positive z axis at doule pendulum pendulum angle 
        state_dict = OrderedDict()
        d = self._config.num_digitized
        vec, vel = obs["orientations"], obs["velocity"]
        arm_vec, pendulum_vec = vec[0:2], vec[2:4]
        arm_vel, pendulum_vel = vel[0], vel[1]
        arm_rad = np.arctan2(arm_vec[1], arm_vec[0])
        pendulum_rad = np.arctan2(pendulum_vec[1], pendulum_vec[0])
        n_arm_rad = np.digitize(arm_rad, np.linspace(-np.pi, np.pi, d +1)[1:-1])
        n_arm_vel = np.digitize(arm_vel.clip(-8, 8), np.linspace(-8, 8, d+1)[1:-1])

        n_pendulum_rad = np.digitize(pendulum_rad, np.linspace(-np.pi, np.pi, d+1)[1:-1] + self._arrange)
        n_pendulum_vel = np.digitize(pendulum_vel.clip(-8, 8), np.linspace(-8, 8, d+1)[1:-1])

        state_dict["arm_rad"] = arm_rad
        state_dict["pendulum_rad"] = pendulum_rad
        state_dict["arm_vel"] = arm_vel
        state_dict["pendulum_vel"] = pendulum_vel
        state_dict["n_arm_rad"] = n_arm_rad
        state_dict["n_pendulum_rad"] = n_pendulum_rad
        state_dict["n_arm_vel"] = n_arm_vel
        state_dict["n_pendulum_vel"] = n_pendulum_vel
        state_dict["digitized_state"] = n_pendulum_rad + n_pendulum_vel*d + n_arm_vel*d**2 + n_arm_rad*d**3
        if n_arm_rad == 0 or n_arm_rad == d - 1:
            done = True
        else:
            done = False
        return state_dict["digitized_state"], done, state_dict


class SysIden():
    def __init__(self, config):
        self._config = config
        self._env = sys_iden(init_alpha=config.init_alpha)
        print('dt = ', config.repeat * self._env.control_timestep())

    @property
    def action_space(self):
        return self._env.action_spec()

    @property
    def obs_space(self):
        return self._env.observation_spec()
    
    def step(self, action, time=None, timedepedence=None):
        for _ in range(self._config.repeat):   
            obs = self._env.step(action).observation
        state_dict, done = self._get_obs(obs)
        reward = 0
        return state_dict, reward, done, state_dict

    def reset(self):
        obs = self._env.reset().observation
        state_dict, done = self._get_obs(obs)
        return state_dict

    def _get_obs(self, obs):
        # 0 is positive z axis at doule pendulum pendulum angle 
        state_dict = OrderedDict()
        vec, vel = obs["orientations"], obs["velocity"]
        arm_vec, pendulum_vec = vec[0:2], vec[2:4]
        arm_vel, pendulum_vel = vel[0], vel[1]
        arm_rad = np.arctan2(arm_vec[1], arm_vec[0])
        pendulum_rad = np.arctan2(pendulum_vec[1], pendulum_vec[0])

        state_dict["theta"] = arm_rad
        state_dict["alpha"] = pendulum_rad
        state_dict["theta_dot"] = arm_vel
        state_dict["alpha_dot"] = pendulum_vel
        done = False
        return state_dict, done


def main():
    from dataclasses import dataclass
    import time 
    from PIL import Image

    @dataclass
    class EnvConfig:
        domain: str = "double_pendulum"
        task: str = "swingup"
        num_digitized: int = 16
        num_action: int = 2
        state_size: int = num_digitized**3
        gamma: float = 0.99
        alpha: float = 0.5
        max_episode: int = int(10e3)
        episode_length: int = 400
        should_log_model: int = (10e3)
        should_log_scalar: int = int(10)
        should_log_video: int = int(50)
        restore: bool = False
        restore_file: str = "Qtable.npy"
        video_length: int = 400
        logdir: str = "./logs/" + str(time.strftime("%Y-%m-%d-%H-%M-%S")) + "/"
    env = SwingUp(EnvConfig())
    # env = suite.load(domain_name="acrobot", task_name="swingup")
    env.reset()
    for i in range(100):
        img = Image.fromarray(env._env.physics.render(height=480, width=640,camera_id=0))
        img.save("./img.png")
        for i in range(10):
            env.step(2)

if __name__ == "__main__":
    main()