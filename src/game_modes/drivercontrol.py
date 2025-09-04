# Library imports
from vex import *

# Project imports
from configuration.robot_config import drivetrain, controller, brain
from configuration.settings import ControllerSettings, DrivetrainSettings

def driver_control_entrypoint():
    '''Executed once upon entering driver control mode'''
    brain.screen.clear_screen()
    brain.screen.print("Running driver control.")
    while True:
        drivetrain_update()
        wait(20, MSEC) # Run the loop every 20 milliseconds (50 times per second)

def drivetrain_update():
    '''To be called repeatedly in driver control mode to update the drivetrain'''
    # Get joystick values with deadzone applied
    forward = controller.get_axis_with_deadzone(ControllerSettings.FORWARD_BACKWARD_AXIS)
    strafe = controller.get_axis_with_deadzone(ControllerSettings.STRAFE_AXIS)
    turn = controller.get_axis_with_deadzone(ControllerSettings.TURN_AXIS)

    # Apply speed modifiers
    forward *= DrivetrainSettings.FORWARD_BACKWARD_SPEED_MODIFIER
    strafe *= DrivetrainSettings.STRAFE_SPEED_MODIFIER
    turn *= DrivetrainSettings.TURN_SPEED_MODIFIER

    # Command the drivetrain to move
    drivetrain.drive(forward, strafe, turn)