from __future__ import absolute_import

from .self_car_velocity import SelfCarVelocity


class LowSpeed(SelfCarVelocity):
    scenario_id = 12004001

    @staticmethod
    def second_check(length):
        return length > 5000

    @staticmethod
    def enter_check(status, speed):
        return status == 0 and 0.1 < speed <= 20

    @staticmethod
    def end_check(status, speed):
        return status == 1 and (speed > 20 or speed <= 0.1)
