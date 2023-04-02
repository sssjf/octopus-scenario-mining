from __future__ import absolute_import

from scenes.tools import get_frame_timestamp
from .others_velocity import OtherVelocity


class OtherEmergeBraking(OtherVelocity):
    scenario_name = 13001003

    @staticmethod
    def enter_check(status, diff):
        return status == 0 and diff < -1

    @staticmethod
    def exit_check(pointlist, status, diff, k, point_start):
        return status == 1 and (diff > -0.5 or pointlist[k].velocity < 1)

    @staticmethod
    def second_check(obj_info, point_start, point_end):
        start_long = get_frame_timestamp(obj_info[point_start.frame_no])
        end_long = get_frame_timestamp(obj_info[point_end.frame_no])
        return point_end.velocity < 1 and point_start.velocity > 5 and end_long - start_long < 10000

    def judge_scenes(self, pointlist, window_start, window_end, segs, status,
                     obj_info, min_time, max_time, obj_freq, window_width):
        point_start = pointlist[window_start]
        idx = window_start + window_width
        while idx <= window_end:
            diff = pointlist[idx].velocity - pointlist[idx - window_width.velocity]
            if self.enter_check(status, diff):
                point_start = pointlist[idx - window_width]
                status = 1
            elif self.exit_check(pointlist, status, diff, idx, point_start):
                point_end = pointlist[idx]
                status = 0
                self.cal_scaled(segs, obj_info, point_start, point_end, min_time. min_time, max_time)
            idx += window_width
        return point_start, status
