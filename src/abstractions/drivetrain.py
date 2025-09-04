from vex import *

class Drivetrain:
    def __init__(
        self,
        left_motor: Motor | MotorGroup,
        right_motor: Motor | MotorGroup,
        strafe_motor: Motor | MotorGroup,
        inertia_sensor: Inertial,
    ):
        self.left_motor = left_motor
        self.right_motor = right_motor
        self.strafe_motor = strafe_motor
        self.inertia_sensor = inertia_sensor

    def drive(self, forward: float, strafe: float, turn: float):
        left_speed = forward + turn
        right_speed = forward - turn
        strafe_speed = strafe

        self.left_motor.spin(FORWARD, left_speed, PERCENT)
        self.right_motor.spin(FORWARD, right_speed, PERCENT)
        self.strafe_motor.spin(FORWARD, strafe_speed, PERCENT)