# Library imports
from vex import *

# Project imports
from abstractions.drivetrain import Drivetrain
from modules.custom_controller import CustomController


# Global instances of motors and sensors
class Motors:
    # Individual drive motors
    left_front_motor = Motor(Ports.PORT19, GearSetting.RATIO_18_1, False)
    left_back_motor = Motor(Ports.PORT20, GearSetting.RATIO_18_1, False)
    right_front_motor = Motor(Ports.PORT11, GearSetting.RATIO_18_1, True)
    right_back_motor = Motor(Ports.PORT13, GearSetting.RATIO_18_1, True)
    
    # Strafing motor
    strafe_motor = Motor(Ports.PORT12, GearSetting.RATIO_18_1, False)
    
    # Motor groups for efficient control
    left_motor_group = MotorGroup(left_front_motor, left_back_motor)
    right_motor_group = MotorGroup(right_front_motor, right_back_motor)

class Sensors:
    inertia_sensor = Inertial(Ports.PORT6)

# Global instance of Controller & Brain
controller = CustomController()
brain = Brain()

# Drivetrain instance using motor groups
drivetrain = Drivetrain(Motors.left_motor_group, Motors.right_motor_group, Motors.strafe_motor, Sensors.inertia_sensor)

