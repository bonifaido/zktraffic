# ==================================================================================================
# Copyright 2014 Twitter, Inc.
# --------------------------------------------------------------------------------------------------
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==================================================================================================


""" Process helpers used to improve zktraffic operation """

import os
import time

from twitter.common import log

try:
  import psutil
  HAS_PSUTIL = True
except ImportError:
  HAS_PSUTIL = False


class PsUtilProcessOptions(object):

    def __init__(self):
        self.process = psutil.Process()

    def set_cpu_affinity(self, cpu_affinity_csv):
        """
        Set CPU affinity for this process
        :param cpu_affinity_csv: A comma-separated string representing CPU cores
        """
        try:
            cpu_list = self.parse_cpu_affinity(cpu_affinity_csv)
            self.process.cpu_affinity(cpu_list)
        except (OSError, ValueError) as e:
            log.warn('unable to set cpu affinity: {}, on process: {}'.format(cpu_affinity_csv, e))
        except AttributeError:
            log.warn('cpu affinity is not available on your platform')

    @property
    def cpu_affinity(self):
        """
        Get CPU affinity of this process
        :return: a list() of CPU cores this processes is pinned to
        """
        try:
          return self.process.cpu_affinity()
        except AttributeError:
          log.warn('cpu affinity is not available on your platform')

    def set_niceness(self, nice_level):
        """
        Set the nice level of this process
        :param nice_level: the nice level to set
        """
        try:
            # TODO (phobos182): double check that psutil does not allow negative nice values
            if not 0 <= nice_level <= 20:
                raise ValueError('nice level must be between 0 and 20')
            self.process.nice(nice_level)
        except (EnvironmentError, ValueError, psutil.AccessDenied, psutil.NoSuchProcess) as e:
            log.warn('unable to set nice level on process: {}'.format(e))

    @property
    def niceness(self):
        """
        Get nice level of this process
        :return: an int() representing the nice level of this process
        """
        return self.process.nice()

    @property
    def uptime(self):
      """
      Current process' uptime in seconds
      """
      return int(time.time()) - int(self.process.create_time())

    @staticmethod
    def parse_cpu_affinity(cpu_affinity_csv):
        """
        Static method to parse a csv string string into a list of integers
        :param cpu_affinity_csv: a CSV of cpu cores to parse
        :return: a list() of integers representing CPU cores
        """
        return [int(_) for _ in cpu_affinity_csv.split(',')]


class DummyProcessOptions(object):
  def set_cpu_affinity(self, _):  # pragma: no cover
    pass

  @property
  def cpu_affinity(self):  # pragma: no cover
    pass

  def set_niceness(self, _):  # pragma: no cover
    pass

  @property
  def niceness(self):  # pragma: no cover
    return 0

  @property
  def uptime(self):  # pragma: no cover
    if os.path.exists("/proc/self"):
      try:
        return int(time.time() - os.stat("/proc/self").st_ctime)
      except Exception:
        pass

    return 0

  @staticmethod
  def parse_cpu_affinity(_):  # pragma: no cover
    return []


ProcessOptions = PsUtilProcessOptions if HAS_PSUTIL else DummyProcessOptions  # pragma: nocover
