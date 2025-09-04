from vex import *
# This file contains settings for the project. You can modify these settings
# as needed for your specific robot configuration and behavior.

class DrivetrainSettings:
    "Drivetrain configuration settings"

    FORWARD_BACKWARD_SPEED_MODIFIER = 1.0  # Modifier for forward/backward speed. Higher values increase speed.
    STRAFE_SPEED_MODIFIER = 1.0             # Modifier for strafing speed. Higher values increase speed.
    TURN_SPEED_MODIFIER = 1.0               # Modifier for turning speed. Higher values increase speed.

class ControllerSettings:
    "Controller configuration settings"

    DEADZONE_THRESHOLD = 5  # Joystick deadzone threshold. Values within this range are ignored to prevent drift.
    
    FORWARD_BACKWARD_AXIS = 2
    STRAFE_AXIS = 1
    TURN_AXIS = 4