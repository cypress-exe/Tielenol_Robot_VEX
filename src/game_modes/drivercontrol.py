# Library imports
from vex import *

# Project imports
from configuration.robot_config import drivetrain, controller, brain
from configuration.settings import ControllerSettings, DrivetrainSettings
from modules.logger import logger, ScreenTarget

# Track last significant input for logging
last_input_log_time = 0

def driver_control_entrypoint():
    '''Executed once upon entering driver control mode'''
    logger.info("=== DRIVER CONTROL MODE STARTED ===", ScreenTarget.BOTH)
    
    try:
        while True:
            drivetrain_update()
            wait(20, MSEC) # Run the loop every 20 milliseconds (50 times per second)
    except Exception as e:
        logger.critical(f"Driver control crashed: {e}")
        logger.critical("Robot stopped for safety", ScreenTarget.BOTH)

def drivetrain_update():
    '''To be called repeatedly in driver control mode to update the drivetrain'''
    global last_input_log_time
    
    # Get joystick values with deadzone applied
    forward = controller.get_axis_with_deadzone(ControllerSettings.FORWARD_BACKWARD_AXIS)
    strafe = controller.get_axis_with_deadzone(ControllerSettings.STRAFE_AXIS)
    turn = controller.get_axis_with_deadzone(ControllerSettings.TURN_AXIS)

    # Log significant inputs occasionally (not every loop to avoid spam)
    current_time = brain.timer.time()
    if (abs(forward) > 50 or abs(strafe) > 50 or abs(turn) > 50) and \
       (current_time - last_input_log_time > 2000):  # Log every 2 seconds max
        logger.debug(f"Driver input: F:{forward:.0f} S:{strafe:.0f} T:{turn:.0f}", ScreenTarget.SILENT)
        last_input_log_time = current_time

    # Apply speed modifiers
    forward *= DrivetrainSettings.FORWARD_BACKWARD_SPEED_MODIFIER
    strafe *= DrivetrainSettings.STRAFE_SPEED_MODIFIER
    turn *= DrivetrainSettings.TURN_SPEED_MODIFIER

    # Command the drivetrain to move
    try:
        drivetrain.drive(forward, strafe, turn)
    except Exception as e:
        logger.error(f"Drivetrain command failed: {e}")