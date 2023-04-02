from __future__ import absolute_import
import math
import time

from scenes.point import Point

vehicle_classifications = [1, 2, 6]


def safe_division(dividend, divisor):
    try:
        return dividend / divisor
    except ZeroDivisionError as error:
        raise error


def get_frame_timestamp(frame):
    return frame["secs"] * 1000 + frame["nsecs"] // 1000000


def get_frame_read_time(frame):
    time_array = time.localtime(frame["secs"])
    return time.strftime("%Y-%m-%d %H-%M-%S", time_array)


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
                abs(obj["y_position"]) < abs(y):
            return False
    return True


def find_frame_by_time(bag, time_stamp):
    for frame in bag:
        if get_frame_timestamp(frame) >= time_stamp:
            return frame
        return bag[0]


def cal_velocity(obj):
    velocity = math.sqrt(
        obj["absolute_velocity_linear_x"] ** 2 + obj["absolute_velocity_linear_y"] ** 2
    )
    return velocity


def cal_angle(obj):
    velocity_x = obj["absolute_velocity_linear_x"]
    velocity_y = obj["absolute_velocity_linear_y"]
    if velocity_y == 0 and velocity_x == 0:
        return 0
    elif velocity_y == 0 and velocity_x > 0:
        return math.pi / 2
    elif velocity_y == 0 and velocity_x < 0:
        return -math.pi / 2
    else:
        return math.atan(safe_division(velocity_x, float(velocity_y)))


def merge_segs(segs):
    # merge the coincide segments
    segs = sorted(segs, key=lambda r: r["start_time"])
    final_segs = []
    if len(segs) > 0:
        temp_start = segs[0]["start_time"]
        temp_end = segs[0]["end_time"]
        scenario_name = segs[0]["scenario_name"]
        for i in range(1, len(segs)):
            if segs[i]["start_time"] > temp_end:
                final_segs.append({"scenario_name": scenario_name,
                                   "start_time": temp_start,
                                   "end_time": temp_end})
                temp_end = segs[i]["end_time"]
                temp_start = segs[i]["start_time"]
            elif segs[i]["end_time"] > temp_end:
                temp_end = segs[i]["end_time"]
        final_segs.append({"scenario_name": scenario_name,
                           "start_time": temp_start,
                           "end_time": temp_end})
    return final_segs


def join_segs(fractions, scenario_name, empty_limit=3000, length_limit=0):
    segs = []
    if len(fractions) > 1:
        last_start = 0
        last_end = 1
        for i in range(2, len(fractions), 2):
            if fractions[i] - fractions[last_end] < empty_limit:
                last_end = i + 1
            else:
                if fractions[last_end] - fractions[last_start] > length_limit:
                    start = fractions[last_start]
                    end = fractions[last_end]
                    segs.append({"scenario_name": scenario_name,
                                 "start_time": start,
                                 "end_time": end})
                last_start = i
                last_end = i + 1
        if fractions[last_end] - fractions[last_start] > length_limit:
            start = fractions[last_start]
            end = fractions[last_end]
            segs.append({"scenario_name": scenario_name,
                         "start_time": start,
                         "end_time": end})
    return segs


def scale_segs(segs, min_time, max_time):
    res = []
    for seg in segs:
        (scale_start, scale_end) = scale_time(seg["start_time"], seg["end_time"], min_time, max_time)
        res.append({"scenario_name": seg["scenario_name"],
                    "start_time": scale_start,
                    "end_time": scale_end})
    return res


def yaw_from_quaternions(w, x, y, z):
    a = 2 * (w * z + x * y)
    b = 1 - 2 * (y * y + z * z)
    return math.atan2(a, b)


def front_same_lane(obj, car):
    return obj["id"] == car[0] and obj["classification"] == car[1] \
        and 0 < obj["x_position"] < 60 and abs(obj["y_position"]) < 2


def in_close_lane(y):
    return abs(y) < 5


def other_obj_valid(obj):
    return obj["classification"] in vehicle_classifications and obj["x_position"] > 0


def add_cars(obj_info):
    size = len(obj_info)
    cars = set()
    for i in range(size):
        for obj in obj_info[i]["object_list"]:
            if other_obj_valid(obj):
                cars.add((obj["id"], obj["classification"]))
    return cars


def get_pointlist_front(obj_info, car, size):
    # get the pointlist of the information for other cars
    pointlist = list()
    for i in range(size):
        for obj in obj_info[i]["object_list"]:
            if front_same_lane(obj, car):
                velocity = cal_velocity(obj)
                angle = cal_angle(obj)
                pointlist.append(
                    Point(obj["id"], obj["x_position"], obj["y_position"],
                          obj["secs"], obj["nsecs"], i, obj["classification"], velocity, angle))
    return pointlist


def get_secs_angles(loc_info):
    loc_size = len(loc_info)
    angles = {}
    angles_this_sec = []

    last_sec = loc_info[0]["secs"]
    for i in range(loc_size):
        this_sec = loc_info[i]["secs"]
        this_angle = yaw_from_quaternions(loc_info[i]["w_orientation"],
                                          loc_info[i]["x_orientation"],
                                          loc_info[i]["y_orientation"],
                                          loc_info[i]["z_orientation"])
        if this_sec != last_sec or i == loc_size - 1:
            angles[last_sec] = safe_division(angles_this_sec[int(len(angles_this_sec) / 20.)] * 180, math.pi)
            angles_this_sec = []
            last_sec = this_sec
        angles_this_sec.append(this_angle)
    angles[last_sec] = safe_division(angles_this_sec[int(len(angles_this_sec) / 2.0)] * 180, math.pi)
    return angles
