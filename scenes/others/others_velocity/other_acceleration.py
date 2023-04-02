from __future__ import absolute_import

from scenes.tools import get_frame_timestamp
from .others_velocity import OtherVelocity


class OtherAcceleration(OtherVelocity):
    scenario_name = 13004001

    @staticmethod
    def enter_check(status, diff):
        return status == 0 and diff > 0.4

    @staticmethod
    def exit_check(pointlist, status, diff, k, point_start):
        return status == 1 and (diff < 0.2 or pointlist[k].velocity < point_start.velocity)

    @staticmethod
    def second_check(obj_info, point_start, point_end):
        start_long = get_frame_timestamp(obj_info[point_start.frame_no])
        end_long = get_frame_timestamp(obj_info[point_end.frame_no])
        return end_long - start_long > 3000 and (
                point_start.velocity > 3 and point_end.velocity - point_start.velocity > 2)

    def judge_scenes(self, pointlist, window_start, window_end, segs, status,
                     obj_info, min_time, max_time, obj_freq, window_width):
        # judge the scene if it is right for the requirement
        point_start = pointlist[window_start]
        k = window_start + window_width
        while k <= window_end:
            diff = pointlist[k].velocity - pointlist[k - window_width].velocity
            if self.enter_check(status, diff):
                point_start = pointlist[k - window_width]
                status = 1
            elif self.exit_check(pointlist, status, diff, k, point_start):
                point_end = pointlist[k]
                status = 0
                self.cal_scaled(segs, obj_info, point_start, point_end, min_time, max_time)
            k += window_width
        return point_start, status
