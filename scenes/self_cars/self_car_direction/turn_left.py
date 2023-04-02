from __future__ import absolute_import

from scenes import Sensor, K_LOG
from scenes.tools import get_frame_timestamp, scale_time, get_secs_angles, merge_segs


class TurnLeft:
    scenario_name = 12001003
    scenario_name_u = 12001005
    threshold = 0
    min_speed = 0.0

    @staticmethod
    def need_topics():
        return [Sensor.VEHICLE, Sensor.EGO_TF]

    @staticmethod
    def match_conditions(frame):
        return frame["steering_angle"] < TurnLeft.threshold \
            and frame["vehicle_speed"] > TurnLeft.min_speed \
            and frame["gear_value"] != 2

    @staticmethod
    def lose_conditions(frame):
        return frame["steering_angle"] >= TurnLeft.threshold \
            or frame["vehicle_speed"] <= TurnLeft.min_speed

    @staticmethod
    def check(raw):
        K_LOG.info("start finding left and u turning scenes...")
        veh_info = raw[Sensor.VEHICLE]
        ego_info = raw[Sensor.EGO_TF]
        size = len(veh_info)
        angles = get_secs_angles(ego_info)

        status = start = 0
        segs = []
        min_time = get_frame_timestamp(veh_info[0])
        max_time = get_frame_timestamp(veh_info[size - 1])

        for x in range(size):
            message = veh_info[x]
            if status == 0 and TurnLeft.match_conditions(message):
                start = x
                status = 1
            elif status == 1 and TurnLeft.lose_conditions(message):
                start_long = get_frame_timestamp(veh_info[start])
                end_long = get_frame_timestamp(veh_info[x])
                status = 0
                (scaled_start, scaled_end) = scale_time(start_long, end_long, min_time, max_time)
                angle_start = angles.get(int(start_long / 1000.0))
                angle_end = angles[int(end_long / 1000.0)]
                if 160 < abs(angle_start - angle_end) < 200:
                    segs.append({"scenario_name": TurnLeft.scenario_name_u,
                                 "start_time": scaled_start,
                                 "end_time": scaled_end})
                elif 45 < abs(angle_start - angle_end) < 315:
                    segs.append({"scenario_name": TurnLeft.scenario_name,
                                 "start_time": scaled_start,
                                 "end_time": scaled_end})
        if status == 1:
            start_long = get_frame_timestamp(veh_info[start])
            end_long = get_frame_timestamp(veh_info[-1])
            (scaled_start, scaled_end) = scale_time(start_long, end_long, min_time, max_time)
            angle_start = angles[int(start_long / 1000.0)]
            angle_end = angles[int(end_long / 1000.0)]
            if 160 < abs(angle_start - angle_end) < 200:
                segs.append({"scenario_name": TurnLeft.scenario_name_u,
                             "start_time": scaled_start,
                             "end_time": scaled_end})
            elif 45 < abs(angle_start - angle_end) < 315:
                segs.append({"scenario_name": TurnLeft.scenario_name,
                             "start_time": scaled_start,
                             "end_time": scaled_end})
        return merge_segs(segs)
