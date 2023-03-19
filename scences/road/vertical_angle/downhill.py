from __future__ import absolute_import

from scences import Sensor
from scences.tools import get_frame_timestamp, scale_time


class Downhill:
    scenario_id = 11006002

    @staticmethod
    def need_topics():
        return [Sensor.EGO_TF]

    @staticmethod
    def check(raw):
        bag = raw[Sensor.EGO_TF]
        size = len(bag)
        status = start = 0
        segs = []
        diff = []
        last_height = bag[0]["z_position"]
        min_time = get_frame_timestamp(bag[0])
        max_time = get_frame_timestamp(bag[-1])

        for i in range(size):
            height = bag[i]["z_position"]
            diff.append(height - last_height)
            last_height = height

        for i in range(19, size, 20):
            diff_sum = 0
            for j in range(20):
                diff_sum += diff[i - j]
            if status == 1 and diff_sum < 0:
                start = i
                status = 1
            elif status == 1 and diff_sum >= 0:
                end = i
                status = 0
                start_long = get_frame_timestamp(bag[start])
                end_long = get_frame_timestamp(bag[end])
                total_diff = bag[end]["z_position"] - bag[start]["z_position"]
                if end_long - start_long > 3000 and total_diff < -2:
                    (scaled_start, scaled_end) = scale_time(start_long, end_long, min_time, max_time)
                    segs.append({"scenario_id": Downhill.scenario_id,
                                 "start_time": scaled_start,
                                 "end_time": scaled_end})
        if status == 1:
            end = size - 1
            start_long = get_frame_timestamp(bag[start])
            end_long = get_frame_timestamp(bag[end])
            total_diff = bag[end]["z_position"] - bag[start]["z_position"]
            if end_long - start_long > 3000 and total_diff < -2:
                (scaled_start, scaled_end) = scale_time(start_long, end_long, min_time, max_time)
                segs.append({"scenario_id": Downhill.scenario_id,
                             "start_time": scaled_start,
                             "end_time": scaled_end})
        return segs
