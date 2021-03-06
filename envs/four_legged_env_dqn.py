import numpy as np
from gym import utils
from gym.envs.mujoco import mujoco_env
import sys, os
class FourLeggedEnv(mujoco_env.MujocoEnv, utils.EzPickle):
    x = 0
    y = 0
    t = 0
    def __init__(self):
        xml_path = os.path.split(os.path.realpath(__file__))[0]+"/../xmls/four-legged.xml"
        print("xml_path:",xml_path)
        mujoco_env.MujocoEnv.__init__(self, "ant.xml", 5)
        utils.EzPickle.__init__(self)

    def step(self, a):
        xposbefore = self.get_body_com("torso")[0]
        yposbefore = self.get_body_com("torso")[1]
        self.do_simulation(a, self.frame_skip)
        xposafter = self.get_body_com("torso")[0]
        yposafter = self.get_body_com("torso")[1]

        '''self.x  = self.x+(xposafter - xposbefore)
        self.y = self.y+(yposafter - yposbefore)
        self.t = self.t + self.dt
        forward_reward = self.x/self.t 
        forward_cost = self.y/self.t'''

        forward_reward = (xposafter - xposbefore)/self.dt
        forward_cost = 0#(yposafter - yposbefore)/self.dt *0.5

        ctrl_cost = 0#.4 * np.square(a).sum()
        contact_cost = 0.3 * 1e-2 * np.sum(np.square(np.clip(self.sim.data.cfrc_ext, -1, 1)))
        survive_reward = 0#1.0 * 0.2
        reward = 2*forward_reward - abs(forward_cost) - ctrl_cost - contact_cost + survive_reward
        state = self.state_vector()
        notdone = np.isfinite(state).all() \
            and state[2] >= 0.2 and state[2] <= 1.0
        done = not notdone
        ob = self._get_obs()
        return ob, reward, done, dict(
            reward_forward=forward_reward,
            forward_cost=abs(forward_cost),
            reward_ctrl=-ctrl_cost,
            reward_contact=-contact_cost,
            reward_survive=survive_reward)

    def _get_obs(self):
        return np.concatenate([
            self.sim.data.qpos.flat[2:],
            self.sim.data.qvel.flat,
            np.clip(self.sim.data.cfrc_ext, -1, 1).flat,
        ])

    def reset_model(self):
        qpos = self.init_qpos + self.np_random.uniform(size=self.model.nq, low=-.1, high=.1)
        qvel = self.init_qvel + self.np_random.randn(self.model.nv) * .1
        self.set_state(qpos, qvel)
        return self._get_obs()

    def viewer_setup(self):
        self.viewer.cam.distance = self.model.stat.extent * 0.5
