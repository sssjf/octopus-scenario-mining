from __future__ import absolute_import

from scences import K_LOG, Sensor
from scences.tools import get_frame_timestamp, get_frame_read_time, scale_time


class Reverse:
    scenario_id = 12001002
    gear_reverse = 2
    speed_threshold = 0.1

    @staticmethod
    def need_topics():
        return [Sensor.VEHICLE]

    @staticmethod
    def match_conditions(frame, status):
        return status == 0 and frame["gear_value"] == Reverse.gear_reverse \
            and abs(frame["vehicle_speed"]) > Reverse.speed_threshold

    @staticmethod
    def lose_conditions(frame, status):
        return status == 1 and (frame["gear_value"] != 2 or abs(frame["vehicle"]) <= 0.1)

    @staticmethod
    def check(raw):
        K_LOG.info("find reverse...")
        veh_info = raw[Sensor.VEHICLE]
        size = len(veh_info)
        time_limit = 1000
        status = start = 0
        segs = []
        min_time = get_frame_timestamp(veh_info[0])
        max_time = get_frame_timestamp(veh_info[size - 1])

        for x in range(size):
            message = veh_info[x]
            if Reverse.match_conditions(message, status):
                start = x
                status = 1
            elif Reverse.lose_conditions(message, status):
                start_long = get_frame_timestamp(veh_info[start])
                end_long = get_frame_timestamp(veh_info[x])
                status = 0
                if end_long - start_long > time_limit:
                    (scaled_start, scaled_end) = scale_time(start_long, end_long, min_time, max_time)
                    segs.append({"scenario_id": Reverse.scenario_id,
                                 "start_time": scaled_start,
                                 "end_time": scaled_end})
        if status == 1:
            start_long = get_frame_timestamp(veh_info[start])
            end_long = get_frame_timestamp(veh_info[size - 1])
            if end_long - start_long > time_limit:
                (scaled_start, scaled_end) = scale_time(start_long, end_long, min_time, max_time)
                segs.append({"scenario_id": Reverse.scenario_id,
                             "start_time": scaled_start,
                             "end_time": scaled_end})
        return segs
