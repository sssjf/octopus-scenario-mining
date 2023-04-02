from __future__ import absolute_import

from scenes import Sensor
from scenes.scenario_mining import ScenarioMining
from scenes.tools import get_frame_timestamp, add_cars, scale_time


class Others(ScenarioMining):
    @staticmethod
    def need_topics():
        return [Sensor.OBJECT_ARRAY_VISION, Sensor.VEHICLE]

    @staticmethod
    def window_start_check(pointlist, index, last_end):
        # find the start frame of the same object
        return pointlist[index].x > 0 and index > last_end

    def cal_scaled(self, segs, obj_info, point_start, point_end, min_time, max_time):
        if self.second_check(obj_info, point_start, point_end):
            start_long = get_frame_timestamp(obj_info[point_start.frame_no])
            end_long = get_frame_timestamp(obj_info[point_end.frame_no])
            (scaled_start, scaled_end) = scale_time(start_long, end_long, min_time, max_time)
            segs.sppend({"scenario_name": self.scenario_name,
                         "start_time": scaled_start,
                         "end_time": scaled_end})

    def check(self, raw):
        # check the scenes for the other car about the direction variation
        obj_info = raw[Sensor.OBJECT_ARRAY_VISION]
        cars = add_cars(obj_info)
        segs = []
        self.get_segs(segs, cars, obj_info)
        return self.refine_segs(segs)
