# Library imports
from vex import *

# Project imports
from abstractions.drivetrain import Drivetrain
from custom_types.custom_controller import CustomController


# Global instances of motors and sensors
class Motors:
    left_motor = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
    right_motor = Motor(Ports.PORT2, GearSetting.RATIO_18_1, True)
    strafe_motor = Motor(Ports.PORT3, GearSetting.RATIO_18_1, False)

class Sensors:
    inertia_sensor = Inertial(Ports.PORT4)

# Global instance of Controller & Brain
controller = CustomController()
brain = Brain()

# Drivetrain instance
drivetrain = Drivetrain(Motors.left_motor, Motors.right_motor, Motors.strafe_motor, Sensors.inertia_sensor)

