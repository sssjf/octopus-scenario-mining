from __future__ import absolute_import

from .self_car_velocity import SelfCarVelocity


class HighSpeed(SelfCarVelocity):
    scenario_name = 12004003

    @staticmethod
    def second_check(length):
        return length > 5000

    @staticmethod
    def enter_check(status, speed):
        return status == 0 and speed >= 60

    @staticmethod
    def exit_check(status, speed):
        return status == 1 and speed < 60
