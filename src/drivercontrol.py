# Library imports
from vex import *

# Project imports
from configuration.robot_config import drivetrain, controller
from configuration.settings import ControllerSettings, DrivetrainSettings


def driver_control_update():
    forward = controller.get_axis_with_deadzone(ControllerSettings.FORWARD_BACKWARD_AXIS)
    strafe = controller.get_axis_with_deadzone(ControllerSettings.STRAFE_AXIS)
    turn = controller.get_axis_with_deadzone(ControllerSettings.TURN_AXIS)

    forward *= DrivetrainSettings.FORWARD_BACKWARD_SPEED_MODIFIER
    strafe *= DrivetrainSettings.STRAFE_SPEED_MODIFIER
    turn *= DrivetrainSettings.TURN_SPEED_MODIFIER

    drivetrain.drive(forward, strafe, turn)