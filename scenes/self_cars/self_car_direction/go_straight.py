from __future__ import absolute_import

import math

from scenes import Sensor, K_LOG
from scenes.tools import yaw_from_quaternions, merge_segs, safe_division


class GoStraight:
    scenario_name = 12001001

    @staticmethod
    def need_topics():
        return [Sensor.VEHICLE, Sensor.EGO_TF]

    @staticmethod
    def get_angle_diffs(loc_info):
        angle_diffs = [(0, 0)]
        last_sec = 0
        last_angle = yaw_from_quaternions(loc_info[0]["w_orientation"],
                                          loc_info[0]["x_orientation"],
                                          loc_info[0]["y_orientation"],
                                          loc_info[0]["z_orientation"])
        last_angle = safe_division(last_angle * 180, math.pi)
        for i in range(1, len(loc_info)):
            if loc_info[i]["secs"] == last_sec:
                continue
            this_angle = yaw_from_quaternions(loc_info[i]["w_orientation"],
                                              loc_info[i]["x_orientation"],
                                              loc_info[i]["y_orientation"],
                                              loc_info[i]["z_orientation"])
            this_angle = safe_division(this_angle * 180, math.pi)
            diff = abs(this_angle - last_angle)
            if diff > 180:
                diff = 360 - diff
            angle_diffs.append((loc_info[i]["secs"], diff))
            last_angle = this_angle
            last_sec = loc_info[i]["secs"]
        return angle_diffs

    @staticmethod
    def generate_secs_speeds(veh_info):
        sec_speed = {}
        last_sec = 0
        for frame in veh_info:
            if not frame["secs"] == last_sec:
                sec_speed[frame["secs"]] = frame["vehicle_speed"]
                last_sec = frame["secs"]
        return sec_speed

    @staticmethod
    def get_speed_by_sec(speed_record, sec):
        if sec not in speed_record:
            return 5
        else:
            return speed_record.get(sec)

    @staticmethod
    def check(raw):
        K_LOG.info("start finding ego car go straight scenes")
        veh_bag = raw[Sensor.VEHICLE]
        loc_bag = raw[Sensor.EGO_TF]
        angle_diffs = GoStraight.get_angle_diffs(loc_bag)
        speed_record = GoStraight.generate_secs_speeds(veh_bag)
        segs = []

        status = start = 0
        turning_points = [angle_diffs[1][0]]
        for sec, diff in angle_diffs:
            if (diff > 3 or GoStraight.get_speed_by_sec(speed_record, sec) <= 1) and status == 0:
                start = sec
                status = 1
            elif status == 1 and diff < 3 and GoStraight.get_speed_by_sec(speed_record, sec) > 1:
                end = sec
                status = 0
                if end - start > 2:
                    turning_points.append(start)
                    turning_points.append(end - 1)
        if status == 1:
            end = angle_diffs[-1][0]
            if end - start > 2:
                turning_points.append(start)
                turning_points.append(end)

        turning_points.append(angle_diffs[-1][0])
        for i in range(1, len(turning_points), 2):
            if turning_points[i] - turning_points[i - 1] > 10:
                start_ts = turning_points[i - 1] * 1000
                end_ts = turning_points[i] * 1000
                segs.append({"scenario_name": GoStraight.scenario_name,
                             "start_time": start_ts,
                             "end_time": end_ts})
        return merge_segs(segs)
