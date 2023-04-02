from __future__ import absolute_import

from scenes.others.others import Others
from scenes.tools import get_bag_freq, get_frame_timestamp, get_pointlist_front


class OtherVelocity(Others):
    def judge_scenes(self, pointlist, window_start, window_end, segs, status,
                     obj_info, min_time, max_time, obj_freq, window_width):
        # judge the scenes if it is right for the requirement
        point_start = pointlist[window_start]
        for k in range(window_start + window_width, window_end + 1):
            if self.enter_check(pointlist, status, k):
                point_start = pointlist[k - window_width]
                status = 1
            elif self.exit_check(pointlist, status, k):
                point_end = pointlist[k]
                status = 0
                self.cal_scaled(segs, obj_info, point_start, point_end, min_time, max_time)
        return point_start, status

    def get_segs(self, segs, cars, obj_info):
        # get the segment of the object scenes
        size = len(obj_info)
        obj_freq = int(get_bag_freq(obj_info))
        window_width = int(obj_freq)
        min_time = get_frame_timestamp(obj_info[0])
        max_time = get_frame_timestamp(obj_info[size - 1])
        for car in cars:
            pointlist = get_pointlist_front(obj_info, car, size)
            window_end = -1
            for i in range(len(pointlist) - 1):
                if self.window_start_check(pointlist, i, window_end):
                    status = 0
                    (window_start, window_end) = self.window_end_check(pointlist, i, obj_freq)
                    (point_start, status) = self.judge_scenes(
                        pointlist, window_start, window_end, segs, status, obj_info,
                        min_time, max_time, obj_freq, window_width)
                    if status == 1:
                        point_end = pointlist[window_end]
                        self.cal_scaled(segs, obj_info, point_start, point_end, min_time, max_time)
