from __future__ import absolute_import
from enum import unique, Enum
import logging
import math

from scences.self_cars.self_car_velocity.lowspeed import LowSpeed
from scences.self_cars.self_car_relation.cutin import Cutin
from scences.self_cars.self_car_relation.cutout import Cutout
from scences.self_cars.self_car_direction.go_straight import GoStraight
from scences.others.others_relation.other_overtake import OtherOverTake
from scences.others.others_velocity.other_acceleration import OtherAcceleration
from scences.others.others_velocity.other_emerge_braking import OtherEmergeBraking
from scences.classification.classification import Classification


K_LOG = logging
trans_coefficient = -1 * math.pi / 2700

analyzers = [LowSpeed(), Cutin(), Cutout(), GoStraight(), OtherOverTake(), OtherAcceleration(), OtherEmergeBraking(),
             Classification()]

class_map = {
    "Car": 1,
    "Truck": 2,
    "Pedestrian": 3,
    "Bi_Tricycle": 5,
    "Bus": 6,
    "unknown": 0
}


def class_trans(name):
    ret = class_map[name]
    if ret:
        return ret
    else:
        return 0


@unique
class Sensor(Enum):
    """
    Enum of Sensor
    """
    CAMERA = 0
    LIDAR = 1
    GNSS = 2
    VEHICLE = 3
    EGO_TF = 4
    OBJECT_ARRAY_VISION = 5
    TRAFFIC_LIGHT_MATCHED = 6
    TAG_RECORD = 7
    PLANING_TRAJECTORY = 8
    PREDICTED_OBJECTS = 9
    CONTROL = 10
    ROUTING_PATH = 11


def read_pb_ego_tf(file):
    with open(file.path, 'rb') as raw_file:
        ego_tf = LocalizationInfo()
        ego_tf.ParseFromString(raw_file.read())
        res = []
        for frame in ego_tf.localization_info:
            res.append({
                "x_position": frame.pose_position_x,
                "y_position": frame.pose_position_y,
                "z_position": frame.pose_position_z,
                "x_orientation": frame.pose_orientation_x,
                "y_orientation": frame.pose_orientation_y,
                "z_orientation": frame.pose_orientation_z,
                "w_orientation": frame.pose_orientation_w,
                "secs": frame.stamp_secs,
                "nsecs": frame.stamp_nsecs,
            })
        return res


def read_pb_vehicle_info(file):
    with open(file.path, 'rb') as raw_file:
        vehicle_info = VehicleInfo()
        vehicle_info.ParseFromString(raw_file.read())
        res = []
        for frame in vehicle_info.vehicle_info:
            res.append({
                "vehicle_speed": frame.vehicle_speed,
                "steering_angle": frame.steering_angle * trans_coefficient,
                "gear_value": frame.gear_value,
                "secs": frame.stamp_secs,
                "nsecs": frame.stamp_nsecs,
            })
        return res


def read_pb_object_vision(file):
    with open(file.path, 'rb') as raw_file:
        frames = TrackedObject()
        frames.ParseFromString(raw_file.read())
        res = []
        for frame in frames.tracked_object:
            objects = []
            for obj in frame.objects:
                objects.append({
                    "id": obj.id,
                    "classification": class_trans(obj.label),
                    "x_position": obj.relative_position_x,
                    "y_position": obj.relative_position_y,
                    "z_position": obj.relative_position_z,
                    "x_abs": obj.pose_position_x,
                    "y_abs": obj.pose_position_y,
                    "z_abs": obj.pose_position_z,
                    "orientation": obj.pose_orientation_yaw,
                    "secs": frame.stamp_secs,
                    "nsecs": frame.stamp_nsecs,
                    "absolute_velocity_linear_x": obj.speed_vector_x,
                    "absolute_velocity_linear_y": obj.speed_vector_y,
                })
            res.append({
                "object_list": objects,
                "secs": frame.stamp_secs,
                "nsecs": frame.stamp_nsecs,
            })
        return res


READER_MAP = {
    'pb,' + Sensor.EGO_TF.name: read_pb_ego_tf,
    'pb,' + Sensor.VEHICLE.name: read_pb_vehicle_info,
    'pb,' + Sensor.OBJECT_ARRAY_VISION.name: read_pb_object_vision,
}
