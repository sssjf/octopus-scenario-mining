from __future__ import absolute_import

from scenes import Sensor
from scenes.scenario_mining import ScenarioMining
from scenes.tools import get_frame_timestamp


class SelfCar(ScenarioMining):
    @staticmethod
    def need_topics():
        return [Sensor.VEHICLE]

    def check(self, raw):
        bag = raw[Sensor.VEHICLE]
        size = len(bag)
        status = start = 0
        min_time = get_frame_timestamp(bag[0])
        max_time = get_frame_timestamp(bag[size - 1])
        return self.get_segs(bag, size, status, start, min_time, max_time)
