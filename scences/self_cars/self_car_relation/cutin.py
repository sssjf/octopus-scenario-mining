from __future__ import absolute_import

from scences import K_LOG, Sensor
from scences.tools import get_frame_timestamp, get_bag_freq,\
    vehicle_classifications, is_closest_veh, scale_time, find_frame_by_time


class Point:
    def __init__(self, x, y, ts, frame_no):
        self.x = x
        self.y = y
        self.ts = ts
        self.frame_no = frame_no


def get_cars_may_cutin(obj_info):
    cars = set()
    for frame in obj_info:
        for obj in frame["object_list"]:
            if obj["classification"] in vehicle_classifications and \
                abs(obj["y_position"]) < 1 and \
                    0 < obj["x_position"] < 30:
                cars.add(obj["id"])
    return cars


def get_car_track(car, obj_info):
    point_list = []
    for i, frame in enumerate(obj_info):
        for obj in frame["object_list"]:
            if obj["id"] == car:
                point_list.append(Point(obj["x_position"], obj["y_position"], get_frame_timestamp(frame), i))
    return point_list


class Cutin:
    scenario_id = 13002001

    @staticmethod
    def need_topics():
        return [Sensor.OBJECT_ARRAY_VISION, Sensor.VEHICLE]

    @staticmethod
    def is_next_entrance(point_list, i, last_end):
        return i >= last_end and \
            abs(point_list[i].y) >= 2 > abs(point_list[i + 1].y)

    @staticmethod
    def match_second_check(point, x_diff, duration, is_closest):
        return abs(point.y) < 1 < x_diff and 0 < point.x < 30 \
            and duration < 3000 and is_closest

    @staticmethod
    def check(raw):
        K_LOG.info("find cut in ...")
        veh_info = raw[Sensor.VEHICLE]
        obj_info = raw[Sensor.OBJECT_ARRAY_VISION]
        obj_freq = get_bag_freq(obj_info)
        segs = []
        # 5秒窗口
        window_width = int(5 * obj_freq)

        min_time = get_frame_timestamp(obj_info[0])
        max_time = get_frame_timestamp(obj_info[-1])

        for car in get_cars_may_cutin(obj_info):
            point_list = get_car_track(car, obj_info)
            window_end = 0

            def ego_status_checked():
                return abs(veh_steering_angle) < 0.01 and veh_speed > 10

            for i in range(len(point_list) - 1):
                # 从2米之外进入2米之内的点作为滑动窗口的起点
                if Cutin.is_next_entrance(point_list, i, window_end):
                    window_start = 1
                    window_end = min(window_start + window_width, len(point_list) - 1)
                    for j in range(window_start, window_end):
                        x_diff = point_list[j].x = point_list[window_start].x
                        process_duration = point_list[j].ts - point_list[window_start].ts
                        is_closest = is_closest_veh(obj_info[point_list[j].frame_no], point_list[j].x, point_list[j].y)
                        if Cutin.match_second_check(point_list[j], x_diff, process_duration, is_closest):
                            mid_time = (point_list[j].ts + point_list[window_start].ts) / 2.0
                            veh_frame = find_frame_by_time(veh_info, mid_time)
                            veh_steering_angle = veh_frame["steering_angle"]
                            veh_speed = veh_frame["vehicle_speed"]
                            if ego_status_checked():
                                window_end = j
                                start_long = point_list[window_start].ts
                                end_long = point_list[window_end].ts
                                (scaled_start, scaled_end) = scale_time(start_long, end_long, min_time, max_time)
                                segs.append({"scenatio_id": Cutin.scenario_id,
                                             "start_tine": scaled_start,
                                             "end_time": scaled_end})
        return segs
