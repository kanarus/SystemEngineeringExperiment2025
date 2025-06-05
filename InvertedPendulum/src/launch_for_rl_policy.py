import time
from dataclasses import dataclass
import pathlib
import numpy as np

from rl.models import Qtable
from utils.logger import Logger
from real.invpen import Invpen
from rl.env import make_env

@dataclass
class EnvConfig:
    domain: str = "double_pendulum"
    task: str = "balance"
    repeat: int = 2
    num_digitized_arm: int = 4
    num_digitized_pendulum: int = 4
    num_action: int = 4
    state_size: int = (num_digitized_arm**2) * (num_digitized_pendulum**2)
    gamma: float = 0.99
    alpha: float = 0.5
    max_episode: int = int(10e7)
    episode_length: int = 500
    should_log_model: int = 10000
    should_log_scalar: int = 200
    should_log_video: int = 10000
    restore: bool = True
    restore_path: str = "./logs/train/05-23-15-30-29/qtable_110000.npy"
    video_length: int = 200
    logdir: str = pathlib.Path().joinpath("./logs/real-by-rl", str(time.strftime("%m-%d-%H-%M-%S")))


class TrainedAgent():
    def __init__(self):
        config = EnvConfig()
        self.config = config
        # pretrained qtable
        self.qtable = Qtable(config)
        self.logger = Logger(config.logdir)
        print(config.restore_path)
        self.qtable.load(config.restore_path)
        self.env = make_env(config)
        self.start = False
        self.data = {'n_alpha': [], 'n_theta': []}

    def _digitized_obs(self, obs):
        '''
        obs[0] theata
        obs[1] alpha
        obs[2] theta dot
        obs[3] alpha dot
        '''
        # d = self.config.num_digitized
        d_arm = self.config.num_digitized_arm
        d_pendulum = self.config.num_digitized_pendulum
        # n_arm_rad = np.digitize(obs[0],
        #                         np.linspace(self.env._arm_limit[0], self.env._arm_limit[1], d +1)[1:-1])
        # n_arm_vel = np.digitize(obs[2].clip(-8, 8), np.linspace(-8, 8, d+1)[1:-1])

        # n_pen_rad = np.digitize(obs[1],
        #                         np.linspace(self.env._pendulum_limit[0], self.env._pendulum_limit[1], d+1)[1:-1] + self.env._arrange)
        # n_pen_vel = np.digitize(obs[3].clip(-8, 8), np.linspace(-8, 8, d+1)[1:-1])
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
        n_arm_rad = np.digitize(obs[0], np.linspace(self.env._arm_limit[0], self.env._arm_limit[1], d_arm +1)[1:-1])
        # n_arm_rad = np.digitize(arm_rad, arm_rad_div[1:-1])
        n_arm_vel = np.digitize(obs[2].clip(-8, 8), np.linspace(-8, 8, d_arm+1)[1:-1])

        # pendulum_rad_div = make_div(self.env._pendulum_limit[0], self.env._pendulum_limit[1], d_pendulum)
        # n_pen_rad = np.digitize(obs[1], pendulum_rad_div[1:-1] + self.env._arrange)
        n_pen_rad = np.digitize(obs[1], np.linspace(self.env._pendulum_limit[0], self.env._pendulum_limit[1], d_pendulum+1)[1:-1] + self.env._arrange)
        n_pen_vel = np.digitize(obs[3].clip(-8, 8), np.linspace(-8, 8, d_pendulum+1)[1:-1])

        state_dict = {}
        state_dict["n_arm_rad"] = n_arm_rad
        state_dict["n_pen_rad"] = n_pen_rad
        state_dict["digitized_state"] = n_pen_rad + n_pen_vel*d_pendulum + n_arm_vel*d_arm**2 + n_arm_rad*d_arm**3
        arm_cond = n_arm_rad == 0 or n_arm_rad >= d_arm - 1
        pen_cond = n_pen_rad == 0 or n_pen_rad >= d_pendulum -1
        if arm_cond or pen_cond:
            # print(n_arm_rad)
            # print(n_pen_rad)
            done = True
        else:
            done = False
        return state_dict["digitized_state"], done, state_dict

    def policy(self, obs):
        if self.start:
                digitized_state, done, state_dict = self._digitized_obs(obs)
                digitized_action = self.qtable.get_action(digitized_state, False)
                torque = self.env._digitized_action[digitized_action]
                self.data['n_alpha'].append(state_dict['n_pen_rad'])
                self.data['n_theta'].append(state_dict['n_arm_rad'])
                if done:
                    return 0
                if abs(obs[0]) > 0.8*np.pi:
                    return 0
                return torque
        else:
            if abs(obs[0]) < 0.8*np.pi and abs(obs[1]) < np.pi/50.0:
                self.start = True
            return 0

    def after_termination_func(self, data):
        data.update({'n_alpha': self.data['n_alpha'], 'n_theta': self.data['n_theta']})
        data = {key: np.array(value) for key, value in data.items()}
        state_seq_img = self.logger.plot2image('state', {'alpha': data['alpha'],
                                                    'theta': data['theta']})
        n_state_seq_img = self.logger.plot2image('n_state', {'n_alpha': data['n_alpha'],
                                                        'n_theta': data['n_theta']})
        statedot_seq_img = self.logger.plot2image('dot_state', {'alphadot': data['alphadot'],
                                                                'thetadot': data['thetadot']})
        act_seq_img = self.logger.plot2image('action', {'torque': data['torque']})
        time_seq_img = self.logger.plot2image('time', {'time': data['time']})
        dt_seq_img = self.logger.plot2image('dt', {'dt': data['dt']})
        alphaf_seq_img = self.logger.plot2image('alphaf', {'alphaf': data['alpha_f']})
        img_dict = {'action': act_seq_img,
                    'state/nodot': state_seq_img,
                    'state/dot': statedot_seq_img,
                    'state/alphaf': alphaf_seq_img,
                    'state/n': n_state_seq_img,
                    'time': time_seq_img,
                    'dt': dt_seq_img}
        self.logger.log_image(img_dict)

def main():

    agent = TrainedAgent()
    my_invpen = Invpen(agent)

    my_invpen.run(sample_time=0.015, simulation_time=120.0, figure=True, logging=True)

if __name__ == "__main__":
    main()