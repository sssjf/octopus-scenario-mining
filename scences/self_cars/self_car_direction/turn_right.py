from __future__ import absolute_import

from scences import Sensor, K_LOG
from scences.tools import get_frame_timestamp, scale_time, get_secs_angles, merge_segs


class TurnRight:
    scenario_id = 12001004
    threshold = 0.0
    min_speed = 0.0

    @staticmethod
    def need_topics():
        return [Sensor.VEHICLE, Sensor.EGO_TF]

    @staticmethod
    def match_conditions(frame):
        return frame["steering_angle"] > TurnRight.threshold \
            and frame["vehicle_speed"] > TurnRight.min_speed \
            and frame["gear_value"] != 2

    @staticmethod
    def lose_conditions(frame):
        return frame["steering_angle"] <= TurnRight.threshold \
            or frame["vehicle_speed"] <= TurnRight.min_speed

    @staticmethod
    def check(raw):
        K_LOG.info("start finding right turning scenes...")
        veh_info = raw[Sensor.VEHICLE]
        ego_info = raw[Sensor.EGO_TF]
        size = len(veh_info)
        angles = get_secs_angles(ego_info)

        status = start = 0
        segs = []
        min_time = get_frame_timestamp(veh_info[0])
        max_time = get_frame_timestamp(veh_info[-1])

        for x in range(size):
            message = veh_info[x]
            if status == 0 and TurnRight.match_conditions(message):
                start = x
                status = 1
            elif status == 1 and TurnRight.lose_conditions(message):
                start_long = get_frame_timestamp(veh_info[start])
                end_long = get_frame_timestamp(veh_info[x])
                status = 0
                (scaled_start, scaled_end) = scale_time(start_long, end_long, min_time, max_time)
                angle_start = angles.get(int(start_long / 1000.0))
                angle_end = angles[int(end_long / 1000.0)]
                if 45 < abs(angle_start - angle_end) < 315:
                    segs.append({"scenario_id": TurnRight.scenario_id,
                                 "start_time": scaled_start,
                                 "end_time": scaled_end})
        if status == 1:
            start_long = get_frame_timestamp(veh_info[start])
            end_long = get_frame_timestamp(veh_info[-1])
            (scaled_start, scaled_end) = scale_time(start_long, end_long, min_time, max_time)
            angle_start = angles[int(start_long / 1000.0)]
            angle_end = angles[int(end_long / 1000.0)]
            if 45 < abs(angle_start - angle_end) < 315:
                segs.append({"scenario_id": TurnRight.scenario_id,
                             "start_time": scaled_start,
                             "end_time": scaled_end})
        return merge_segs(segs)
