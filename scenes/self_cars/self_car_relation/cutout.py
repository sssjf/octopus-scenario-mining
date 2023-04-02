from __future__ import absolute_import

from scenes import Sensor
from scenes.tools import get_frame_timestamp, get_bag_freq, \
    vehicle_classifications, is_closest_veh, scale_time, find_frame_by_time


def ego_go_straight(veh_frame):
    return abs(veh_frame["steering_angle"]) < 0.01 and veh_frame["vehicle_speed"] > 10


class Point:
    def __init__(self, x, y, ts, frame_no):
        self.x = x
        self.y = y
        self.ts = ts
        self.frame_no = frame_no


class Cutout:
    scenario_name = 13001001

    @staticmethod
    def need_topics():
        return [Sensor.OBJECT_ARRAY_VISION, Sensor.VEHICLE]

    @staticmethod
    def is_next_entrance(pointlist, i, last_end):
        return i > last_end and abs(pointlist[i].y) <= 1 < abs(pointlist[i + 1].y) and 0 < pointlist[i].x < 30

    @staticmethod
    def match_second_check(point, x_diff, duration, is_closest):
        return abs(point.y) > 2 and 0 < point.x < 30 and x_diff > 1 and duration < 3000 and is_closest

    @staticmethod
    def get_cars_may_cut_out(obj_info):
        cars = set()
        for frame in obj_info:
            for obj in frame["object_list"]:
                if abs(obj["y_position"]) < 1 and 0 < obj["x_position"] < 30 and \
                        obj["classification"] in vehicle_classifications:
                    cars.add(obj["id"])
        return cars

    @staticmethod
    def get_car_track(car, obj_info):
        pointlist = []
        for i, frame in enumerate(obj_info):
            for obj in frame["object_list"]:
                if obj["id"] == car:
                    pointlist.append(Point(obj["x_position"], obj["y_position"], get_frame_timestamp(frame), i))
        return pointlist

    @staticmethod
    def check(raw):
        veh_info = raw[Sensor.VEHICLE]
        obj_info = raw[Sensor.OBJECT_ARRAY_VISION]
        min_time = get_frame_timestamp(obj_info[0])
        max_time = get_frame_timestamp(obj_info[-1])
        obj_freq = get_bag_freq(obj_info)
        segs = []
        window_width = int(5 * obj_freq)

        for car in Cutout.get_cars_may_cut_out(obj_info):
            pointlist = Cutout.get_car_track(car, obj_info)
            window_end = 0

            for i in range(len(pointlist) - 1):
                if Cutout.is_next_entrance(pointlist, i, window_end):
                    window_start = i
                    window_end = min(window_start + window_width, len(pointlist) - 1)
                    for j in range(window_start, window_end):
                        x_diff = pointlist[j].x - pointlist[window_start].x
                        process_duration = pointlist[j].ts - pointlist[window_start].ts
                        is_closest = is_closest_veh(
                            obj_info[pointlist[j].frame_no],
                            pointlist[j].x,
                            pointlist[j].y)
                        if Cutout.match_second_check(pointlist[j], x_diff, process_duration, is_closest):
                            mid_time = (pointlist[j].ts + pointlist[window_start].ts) / 2.0
                            veh_frame = find_frame_by_time(veh_info, mid_time)
                            if ego_go_straight(veh_frame):
                                window_end = j
                                start_long = pointlist[window_start].ts
                                end_long = pointlist[window_end].ts
                                (scaled_start, scaled_end) = scale_time(start_long, end_long, min_time, max_time)
                                segs.append({"scenario_name": Cutout.scenario_name,
                                             "start_time": scaled_start,
                                             "end_time": scaled_end})
                                break
        return segs
