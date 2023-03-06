from __future__ import absolute_import
import math
import time

from scences.point import Point

vehicle_classifications = [1, 2, 6]


def safe_division(dividend, divisor):
    try:
        return dividend / divisor
    except ZeroDivisionError as error:
        raise error


def get_frame_timestamp(frame):
    return frame["secs"] * 1000 + frame["nsecs"] // 1000000


def scale_time(start, end, min_time, max_time, length=10000):
    if end - start < length:
        add = (length - start + end) / 2.0
        new_start = int(max(min_time, start - add))
        new_end = int(min(max_time, end + add))
        return new_start, new_end
    else:
        return start, end


def get_bag_freq(bag):
    duration = get_frame_timestamp(bag[-1]) - get_frame_timestamp(bag[0])
    sec_freq = safe_division(len(bag) * 1000, float(duration))
    return sec_freq


def is_closest_veh(frame, x, y):
    for obj in frame["object_list"]:
        if obj["classification"] in vehicle_classifications and \
                obj["x_position"] * x > 0 and \
                obj["y_position"] * y and \
                abs(obj["x_position"]) < abs(x) and \
                abs(obj["y_position"]) < ans(y):
            return False
    return True


def find_frame_by_time(bag, time_stamp):
    for frame in bag:
        if get_frame_timestamp(frame) >= time_stamp:
            return frame
        return bag[0]


def merge_segs(segs):
    # merge the coincide segments
    segs = sorted(segs, key=lambda r: r["start_time"])
    final_segs = []
    if len(segs) > 0:
        temp_start = segs[0]["start_time"]
        temp_end = segs[0]["end_time"]
        scenario_id = segs[0]["scenario_id"]
        for i in range(1, len(segs)):
            if segs[i]["start_time"] > temp_end:
                final_segs.append({"scenario_id": scenario_id,
                                   "start_time": temp_start,
                                   "end_time": temp_end})
                temp_end = segs[i]["end_time"]
                temp_start = segs[i]["start_time"]
            elif segs[i]["end_time"] > temp_end:
                temp_end = segs[i]["end_time"]
        final_segs.append({"scenario_id": scenario_id,
                           "start_time": temp_start,
                           "end_time": temp_end})
    return final_segs


def yaw_from_quaternions(w, x, y, z):
    a = 2 * (w * z + x * y)
    b = 1 - 2 * (y * y + z * z)
    return math.atan2(a, b)
