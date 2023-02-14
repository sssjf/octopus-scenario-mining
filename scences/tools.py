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
