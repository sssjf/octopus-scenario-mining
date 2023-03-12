from __future__ import absolute_import

from scences import Sensor
from scences.tools import get_frame_timestamp, join_segs, scale_segs

class_id = {
    1: 14006001,
    2: 14006002,
    5: 14008001,
    3: 14004001,
    6: 14006003
}


class TimeClasses:
    def __init__(self, ts, classes):
        self.ts = ts
        self.classes = classes


class ClassInfo:
    def __init__(self, ts, status):
        self.ts = ts
        self.status = status
        self.res = []


def record_objs(obj_inf0):
    obj_record = []
    for frame in obj_inf0:
        classes = set()
        for obj in frame["object_list"]:
            if 0 < obj['x_position'] < 60 and abs(obj["y_position"]) < 5:
                classes.add(obj["classification"])
        obj_record.append(TimeClasses(get_frame_timestamp(frame), classes))
    return obj_record


class Classification:
    @staticmethod
    def need_topics():
        return [Sensor.OBJECT_ARRAY_VISION]

    def check(self, raw):
        obj_info = raw[Sensor.OBJECT_ARRAY_VISION]
        obj_record = record_objs(obj_info)
        min_time = get_frame_timestamp(obj_info[0])
        max_time = get_frame_timestamp(obj_info[-1])
        start_stamp = get_frame_timestamp(obj_info[0])
        class_info = {
            1: ClassInfo(start_stamp, 0),
            2: ClassInfo(start_stamp, 0),
            5: ClassInfo(start_stamp, 0),
            3: ClassInfo(start_stamp, 0),
            6: ClassInfo(start_stamp, 0)
        }
        for frame in obj_record:
            for clazz, clazz_id in class_id.items():
                exist = clazz in frame.classes
                info = class_info[clazz]
                if exist and info.status == 0:
                    info.status = 1
                    info.ts = frame.ts
                elif not exist and info.status == 1:
                    start = info.ts
                    end = frame.ts
                    info.status = 0
                    if end - start > 3000:
                        info.res.append(
                            {"scenario_id": clazz_id,
                             "start_time": start,
                             "end_time": end})
        output = []
        for clazz, clazz_id in class_id.items():
            info = class_info[clazz]
            if info.status == 1:
                start = info.ts
                end = obj_record[-1].ts
                info.status = 0
                if end - start > 3000:
                    info.res.append(
                        {"scenario_id": clazz_id,
                         "start_time": start,
                         "end_time": end})
            fractions = []
            for seg in info.res:
                fractions.append(seg["start_time"])
                fractions.append(seg["end_time"])
            output.extend(
                scale_segs(join_segs(fractions, class_id[clazz]), min_time, max_time)
            )
        return output
