# Copyright 2017 The dm_control Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or  implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

"""Acrobot domain."""

import collections

from dm_control import mujoco
from dm_control.rl import control
from dm_control.suite import base
from dm_control.suite import common
from dm_control.utils import containers
from dm_control.utils import rewards
import numpy as np
from pathlib import Path

_DEFAULT_TIME_LIMIT = 10
_CONTROL_TIMESTEP = .01 # Hz
SUITE = containers.TaggedTasks()

_MULTI_PENDULUM = Path(__file__).parent / 'acrobot.xml'

def get_model_and_assets():
  """Returns a tuple containing the model XML string and a dict of assets."""
  return common.read_model(_MULTI_PENDULUM), common.ASSETS


@SUITE.add('benchmarking')
def swingup(time_limit=_DEFAULT_TIME_LIMIT, random=None,
            environment_kwargs=None):
  """Returns Acrobot balance task."""
  physics = Physics.from_xml_string(*get_model_and_assets())
  task = Balance(sparse=False, do_swing=True, random=random)
  environment_kwargs = environment_kwargs or {}
  return control.Environment(
      physics, task, time_limit=time_limit, control_timestep=_CONTROL_TIMESTEP, **environment_kwargs)

@SUITE.add('benchmarking')
def balance(time_limit=_DEFAULT_TIME_LIMIT, random=None,
            environment_kwargs=None):
  """Returns Acrobot balance task."""
  physics = Physics.from_xml_string(*get_model_and_assets())
  task = Balance(sparse=False, do_swing=False, random=random)
  environment_kwargs = environment_kwargs or {}
  return control.Environment(
      physics, task, time_limit=time_limit, control_timestep=_CONTROL_TIMESTEP, **environment_kwargs)

@SUITE.add('benchmarking')
def sys_iden(init_alpha, time_limit=_DEFAULT_TIME_LIMIT, random=None,
            environment_kwargs=None):
  """Returns Acrobot balance task."""
  physics = Physics.from_xml_string(*get_model_and_assets())
  task = SysIden(init_alpha=init_alpha, random=random)
  environment_kwargs = environment_kwargs or {}
  return control.Environment(
      physics, task, time_limit=time_limit, control_timestep=_CONTROL_TIMESTEP, **environment_kwargs)


class Physics(mujoco.Physics):
  """Physics simulation with additional features for the Acrobot domain."""

  def horizontal(self):
    """Returns horizontal (x) component of body frame z-axes."""
    return self.named.data.xmat[['upper_arm', 'lower_arm'], 'xz']

  def vertical(self):
    """Returns vertical (z) component of body frame z-axes."""
    return self.named.data.xmat[['upper_arm', 'lower_arm'], 'zz']

  def to_target(self):
    """Returns the distance from the tip to the target."""
    tip_to_target = (self.named.data.site_xpos['target'] -
                     self.named.data.site_xpos['tip'])
    return np.linalg.norm(tip_to_target)

  def orientations(self):
    """Returns the sines and cosines of the pole angles."""
    elbow_rad = self.named.data.qpos['elbow']
    elbow_cos, elbow_sin = np.cos(elbow_rad), np.sin(elbow_rad)
    shoulder_rad = self.named.data.qpos['shoulder']
    shoulder_cos, shoulder_sin = np.cos(shoulder_rad), np.sin(shoulder_rad)
    return np.concatenate((shoulder_cos, shoulder_sin, elbow_cos, elbow_sin))


class Balance(base.Task):
  """An Acrobot `Task` to  balance the pole."""

  def __init__(self, sparse, do_swing=False, random=None):
    """Initializes an instance of `Balance`.

    Args:
      sparse: A `bool` specifying whether to use a sparse (indicator) reward.
      random: Optional, either a `numpy.random.RandomState` instance, an
        integer seed for creating a new `RandomState`, or None to select a seed
        automatically (default).
    """
    self._sparse = sparse
    self._do_swing = do_swing
    super().__init__(random=random)

  def initialize_episode(self, physics):
    """Sets the state of the environment at the start of each episode.

    Shoulder and elbow are set to a random position between [-pi, pi).

    Args:
      physics: An instance of `Physics`.
    """
    if self._do_swing:
      physics.named.data.qpos[
          ['elbow']] = self.random.uniform(-0.5*np.pi, 0.5*np.pi, 1)
    else:
      physics.named.data.qpos[
          ['elbow']] = self.random.uniform(-(1/10)*np.pi, (1/10)*np.pi, 1) 
    physics.named.data.qpos[
        ['shoulder']] = self.random.uniform(-0, 0, 1)
    # self.random.uniform(-np.pi, np.pi, 2)
    super().initialize_episode(physics)

  def get_observation(self, physics):
    """Returns an observation of pole orientation and angular velocities."""
    obs = collections.OrderedDict()
    obs['orientations'] = physics.orientations()
    obs['velocity'] = physics.velocity()
    return obs

  def _get_reward(self, physics, sparse):
    target_radius = physics.named.model.site_size['target', 0]
    return rewards.tolerance(physics.to_target(),
                             bounds=(0, target_radius),
                             margin=0 if sparse else 1)

  def get_reward(self, physics):
    """Returns a sparse or a smooth reward, as specified in the constructor."""
    return self._get_reward(physics, sparse=self._sparse)

class SysIden(base.Task):
  """An Acrobot `Task` to swing up and balance the pole."""

  def __init__(self, init_alpha=0.25*np.pi, random=None):
    """Initializes an instance of `Balance`.

    Args:
      sparse: A `bool` specifying whether to use a sparse (indicator) reward.
      random: Optional, either a `numpy.random.RandomState` instance, an
        integer seed for creating a new `RandomState`, or None to select a seed
        automatically (default).
    """
    self._init_alpha = init_alpha
    super().__init__(random=random)

  def initialize_episode(self, physics):
    """Sets the state of the environment at the start of each episode.

    Shoulder and elbow are set to a random position between [-pi, pi).

    Args:
      physics: An instance of `Physics`.
    """

    physics.named.data.qpos[['elbow']] = self._init_alpha
    physics.named.data.qpos[['shoulder']] = 0.
    # self.random.uniform(-np.pi, np.pi, 2)
    super().initialize_episode(physics)

  def get_observation(self, physics):
    """Returns an observation of pole orientation and angular velocities."""
    obs = collections.OrderedDict()
    obs['orientations'] = physics.orientations()
    obs['velocity'] = physics.velocity()
    return obs

  def _get_reward(self, physics, sparse):
    target_radius = physics.named.model.site_size['target', 0]
    return rewards.tolerance(physics.to_target(),
                             bounds=(0, target_radius),
                             margin=0 if sparse else 1)

  def get_reward(self, physics):
    """Returns a sparse or a smooth reward, as specified in the constructor."""
    return self._get_reward(physics, sparse=True)