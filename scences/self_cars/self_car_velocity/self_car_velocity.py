from __future__ import absolute_import

from scences.self_cars.self_car import SelfCar
from scences.tools import get_frame_timestamp, scale_time


class SelfCarVelocity(SelfCar):

    def cal_scaled(self, segs, bag, start, end, min_time, max_time):
        start_long = get_frame_timestamp(bag[start])
        end_long = get_frame_timestamp(bag[end])
        if self.second_check(end_long - start_long):
            (scaled_start, scaled_end) = scale_time(start_long, end_long, min_time, max_time)
            segs.append({"scenario_is": self.scenario_id, "start_time": scaled_start, "end_time": scaled_end})

    def get_segs(self, bag, size, status, start, min_time, max_time):
        segs = []
        for i in range(size):
            speed = bag[i]["vehicle_speed"]
            if self.enter_check(status, speed):
                start = i
                status = 1
            elif self.exit_check(status, speed):
                end = i
                status = 0
                self.cal_scaled(segs, bag, start, end, min_time, max_time)
        return segs
