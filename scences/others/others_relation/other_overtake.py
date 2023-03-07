from __future__ import absolute_import

from scences import Sensor, K_LOG
from scences.tools import get_frame_timestamp, get_bag_freq, vehicle_classifications, in_close_lane, \
    find_frame_by_time, cal_velocity, scale_time, merge_segs


class Point:
    def __init__(self, x, y, sec, frame_no, velocity):
        self.x = x
        self.y = y
        self.sec = sec
        self.frame_no = frame_no
        self.velocity = velocity


def get_car_traces(obj_info):
    car_traces = {}
    for i, frame in enumerate(obj_info):
        for obj in frame["object_list"]:
            if obj["classification"] in vehicle_classifications and in_close_lane(obj["y_position"]):
                if obj["id"] not in car_traces:
                    car_traces[obj["id"]] = []
                car_traces[obj["id"]].append(Point(obj["x_position"],
                                                   obj["y_position"],
                                                   frame["secs"],
                                                   i, cal_velocity(obj)))
    return car_traces


def is_next_entrance(pointlist, i, last_end):
    return i >= last_end and pointlist[i].x <= -2 < pointlist[i + 1].x


def end_overtake(this_x, next_x, is_close):
    return this_x <= 2 < next_x and is_close


def whole_check(speed, target_speed):
    return speed > 5 and target_speed > 5


class OtherOverTake:
    scenario_id = 13002002

    @staticmethod
    def need_topics():
        return [Sensor.OBJECT_ARRAY_VISION, Sensor.VEHICLE]

    @staticmethod
    def check(raw):
        K_LOG.info("start finding side car overtake scenes")
        veh_info = raw[Sensor.VEHICLE]
        obj_info = raw[Sensor.OBJECT_ARRAY_VISION]
        min_time = get_frame_timestamp(obj_info[0])
        max_time = get_frame_timestamp(obj_info[-1])
        obj_freq = get_bag_freq(obj_info)
        segs = []
        window_width = int(10 * obj_freq)
        traces = get_car_traces(obj_info)

        for _, points in traces.items():
            window_end = 0
            for i in range(len(points) - 1):
                if is_next_entrance(points, i, window_end):
                    window_start = i
                    window_end = min(window_start + window_width, len(points) - 1)
                    for j in range(window_start, window_end):
                        if points[j + 1].sec - points[j].sec > 1:
                            window_end = j
                            break
                        if end_overtake(points[j].x, points[j + 1].x, in_close_lane(points[j + 1].y)):
                            start_long = get_frame_timestamp(obj_info[points[window_start].frame_no])
                            end_long = get_frame_timestamp(obj_info[points[window_start].frame_no])
                            mid_time = int((start_long + end_long) / 2.0)
                            veh_frame = find_frame_by_time(veh_info, mid_time)
                            speed = veh_frame["vehivle_speed"] / 3.6
                            if whole_check(speed, points[i].velocity):
                                (scaled_start, scaled_end) = scale_time(start_long, end_long, min_time, max_time)
                                segs.append({"scenario_id": OtherOverTake.scenario_id,
                                             "start_time": scaled_start,
                                             "end_time": scaled_end})
                            break
        return merge_segs(segs)
