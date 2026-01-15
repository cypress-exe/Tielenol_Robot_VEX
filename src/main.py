# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py (Monolithic)                                         #
# 	Author:       Dirk                                                         #
# 	Created:      9/4/2025, 2:20:48 PM                                         #
# 	Description:  V5 project - All modules combined into single file           #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *

# ============================================================================
# TYPES
# ============================================================================
class AllianceColor:
    def __init__(self, color_name: str = "UNKNOWN"):
        if isinstance(color_name, str):
            if color_name.upper() in ['RED', 'BLUE', 'UNKNOWN']:
                self.__color_name = color_name.upper()
            else:
                raise ValueError("Invalid color name. Choose 'RED', 'BLUE', or 'UNKNOWN'.")
        elif isinstance(color_name, AllianceColor):
            self.__color_name = color_name.color_name
        else:
            raise TypeError("Color name must be a string.")
        
    def set_to_default(self):
        self.__color_name = "RED"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AllianceColor):
            return self.__color_name == other.__color_name
        return False

    def __ne__(self, other: object) -> bool:
        if isinstance(other, AllianceColor):
            return self.__color_name != other.__color_name
        return True
    
    def __invert__(self):
        if self.__color_name == 'UNKNOWN':
            return AllianceColor('UNKNOWN')
        
        if self.__color_name == 'RED':
            return AllianceColor('BLUE')
        else:
            return AllianceColor('RED')
    
    def __str__(self) -> str:
        return self.__color_name
    
    def __hash__(self) -> int:
        return hash(self.__color_name)
    
class Side:
    def __init__(self, default):
        self.set(default)
        
    def set(self, value):
        if isinstance(value, Side):
            self.__side = value.__side
        elif value.upper() in ['LEFT', 'RIGHT']:
            self.__side = value.upper()
        else:
            raise ValueError("Invalid side name. Choose 'LEFT' or 'RIGHT'.")
        
    def __invert__(self):
        if self.__side == 'LEFT':
            self.__side = 'RIGHT'
        else:
            self.__side = 'LEFT'

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Side):
            return self.__side == value.__side
        if isinstance(value, str):
            return self.__side.lower() == value.lower()
        return False
    
    def __str__(self) -> str:
        return self.__side
    
    def __ne__(self, value: object) -> bool:
        if isinstance(value, Side):
            return self.__side != value.__side
        if isinstance(value, str):
            return self.__side.lower() != value.lower()
        return True
    
    def __hash__(self) -> int:
        return hash(self.__side)

    

# =============================================================================
# SETTINGS CONFIGURATION
# =============================================================================

class DrivetrainSettings:
    """Drivetrain configuration settings"""
    FORWARD_BACKWARD_SPEED_MODIFIER = 1.0   # Modifier for forward/backward speed. Higher values increase speed.
    STRAFE_SPEED_MODIFIER = 1.0             # Modifier for strafing speed. Higher values increase speed.
    TURN_SPEED_MODIFIER = 0.7              # Modifier for turning speed. Higher values increase speed.

class ControllerSettings:
    """Controller configuration settings"""
    DEADZONE_THRESHOLD = 5  # Joystick deadzone threshold. Values within this range are ignored to prevent drift.
    
    FORWARD_BACKWARD_AXIS = 3
    TURN_AXIS = 1
    # =============================== Autonomous ===============================
    LEFT_SIDE_SELECTION_BUTTON = "Left"
    RIGHT_SIDE_SELECTION_BUTTON = "Right"

    # ============================== Drivercontrol ==============================
    STRAFE_LEFT_BUTTON = "Left"
    STRAFE_RIGHT_BUTTON = "Right"

    # Fine Control buttons
    FC_FORWARD_BUTTON = "Up"
    FC_BACKWARD_BUTTON = "Down"

    INTAKE_BUTTON = 'R1'
    OUTPUT_LOW_BUTTON = 'R2'
    OUTPUT_MEDIUM_BUTTON = 'L2'
    OUTPUT_HIGH_BUTTON = 'L1'

    DESCORER_TRIGGER_BUTTON = 'X'
    MATCH_LOAD_UNLOADER_TOGGLE_BUTTON = 'Y'

    COLOR_SWITCH_BUTTON = "A"  # Button to switch alliance color
    BRAKING_SWITCH_BUTTON = "B"  # Button to switch braking mode

class RobotState:
    """Robot state configuration. Edited by the main program."""
    # =========================== CONFIGURED SETTINGS ===========================
    # Edit these values to change the initial robot configuration

    current_alliance_color = AllianceColor("red")  # Default alliance color: 'RED' or 'BLUE'
    current_braking_mode = COAST # Braking mode for drivetrain motors: BRAKE, COAST, or HOLD
    starting_side = Side("RIGHT") # Starting side for autonomous: 'LEFT' or 'RIGHT'
    


# =============================================================================
# LOGGING SYSTEM
# =============================================================================

# Log levels in order of severity
class LogLevel:
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5

# Screen output targets
class ScreenTarget:
    BRAIN = 1
    CONTROLLER = 2
    BOTH = 3

class Logger:
    def __init__(self, brain_instance: Brain, controller_instance: Controller, max_brain_lines=12):
        self.brain = brain_instance
        self.controller = controller_instance
        self.current_log_level = LogLevel.INFO
        
        # Screen management
        self.brain_line = 1
        self.max_brain_lines = max_brain_lines
        
        # Flag to disable brain screen logging (used when config screen is active)
        self.brain_logging_enabled = True

    def set_log_level(self, level):
        """Set the minimum log level that will be processed"""
        self.current_log_level = level
        level_names = {1: "DEBUG", 2: "INFO", 3: "WARNING", 4: "ERROR", 5: "CRITICAL"}
        if level in level_names:
            level_name = level_names[level]
        else:
            level_name = 'UNKNOWN'
        self.info("Log level set to " + level_name)

    def get_log_level(self):
        """Get the current log level"""
        return self.current_log_level

    def _should_log(self, level):
        """Check if a message should be logged based on current log level"""
        return level >= self.current_log_level

    def _log_to_brain(self, message: str):
        """Log message to brain screen with wrapping"""
        # Split message into sections of 48 characters
        segments = []
        while len(message) > 48:
            segments.append(message[:48])
            message = message[48:]
        if message:
            segments.append(message)

        if not self.brain_logging_enabled:
            return

        if self.brain_line > self.max_brain_lines:
            self.brain_line = 1
            self.brain.screen.clear_screen()
        
        self.brain.screen.set_cursor(self.brain_line, 1)
        for segment in segments:
            self.brain.screen.print(segment)
            self.brain.screen.new_line()
            self.brain_line += 1

    def _log_to_controller(self, message: str):
        """Log message to controller screen (single line, overwrites)"""
        self.controller.screen.clear_line(1)
        self.controller.screen.set_cursor(1, 1)
        self.controller.screen.print(message)

    def _format_message(self, level, message):
        """Format message with timestamp and log level"""
        level_names = {1: "DEBUG", 2: "INFO", 3: "WARNING", 4: "ERROR", 5: "CRITICAL"}
        if level in level_names:
            level_name = level_names[level]
        else:
            level_name = 'UNKNOWN'
        return "[" + level_name + "] " + message

    def _log_internal(self, level, message, screen_target=ScreenTarget.BOTH):
        """Internal logging function"""
        if not self._should_log(level):
            return

        formatted_message = self._format_message(level, message)
        
        # Screen output
        if screen_target == ScreenTarget.BRAIN:
            self._log_to_brain(formatted_message)
        elif screen_target == ScreenTarget.CONTROLLER:
            self._log_to_controller(message)
        elif screen_target == ScreenTarget.BOTH:
            self._log_to_brain(formatted_message)
            self._log_to_controller(message)

    # Public logging methods
    def debug(self, message, screen_target=ScreenTarget.BRAIN):
        """Log debug message"""
        self._log_internal(LogLevel.DEBUG, message, screen_target)

    def info(self, message, screen_target=ScreenTarget.BOTH):
        """Log info message"""
        self._log_internal(LogLevel.INFO, message, screen_target)

    def warning(self, message, screen_target=ScreenTarget.BOTH):
        """Log warning message"""
        self._log_internal(LogLevel.WARNING, message, screen_target)

    def error(self, message, screen_target=ScreenTarget.BOTH):
        """Log error message"""
        self._log_internal(LogLevel.ERROR, message, screen_target)

    def critical(self, message, screen_target=ScreenTarget.BOTH):
        """Log critical message"""
        self._log_internal(LogLevel.CRITICAL, message, screen_target)



# =============================================================================
# CUSTOM COMPONENTS
# =============================================================================

class CustomController(Controller):
    def get_axis(self, axis):
        """Returns the specified axis of the controller"""
        if axis == 1:
            return self.axis1
        elif axis == 2:
            return self.axis2
        elif axis == 3:
            return self.axis3
        elif axis == 4:
            return self.axis4
        else:
            raise ValueError("Invalid axis")
            
    def get_axis_with_deadzone(self, axis):
        """Returns the specified axis of the controller with deadzone applied"""
        value = self.get_axis(axis).position()
        if abs(value) < ControllerSettings.DEADZONE_THRESHOLD:
            return 0
        return value
    
    def get_button(self, button_name):
        """Returns the specified button of the controller"""
        if button_name == 'A':
            return self.buttonA
        elif button_name == 'B':
            return self.buttonB
        elif button_name == 'X':
            return self.buttonX
        elif button_name == 'Y':
            return self.buttonY
        elif button_name == 'L1':
            return self.buttonL1
        elif button_name == 'L2':
            return self.buttonL2
        elif button_name == 'R1':
            return self.buttonR1
        elif button_name == 'R2':
            return self.buttonR2
        elif button_name == 'Up':
            return self.buttonUp
        elif button_name == 'Down':
            return self.buttonDown
        elif button_name == 'Left':
            return self.buttonLeft
        elif button_name == 'Right':
            return self.buttonRight
        else:
            raise ValueError("Invalid button name")

class WheelMotor(Motor):
    def __init__(self, port, gear_setting=GearSetting.RATIO_18_1, reversed=False, wheel_diameter_mm=100.0):
        super().__init__(port, gear_setting, reversed)
        self.wheel_diameter_mm: float = wheel_diameter_mm

class WheelMotorGroup(MotorGroup):
    def __init__(self, *motors: WheelMotor):
        super().__init__(*motors)

        if [obj.wheel_diameter_mm for obj in motors].count(motors[0].wheel_diameter_mm) != len(motors):
            raise ValueError("All motors in WheelMotorGroup must have the same wheel_diameter_mm")
        
        self.wheel_diameter_mm: float = motors[0].wheel_diameter_mm if motors else 100.0



# =============================================================================
# DRIVETRAIN ABSTRACTION
# =============================================================================

class Drivetrain:
    def __init__(
        self,
        left_motor: WheelMotorGroup | WheelMotor,
        right_motor: WheelMotorGroup | WheelMotor,
        strafe_motor: WheelMotorGroup | WheelMotor,
        inertia_sensor: Inertial,
    ):
        """
        Initialize drivetrain with motor groups for efficient control
        
        Args:
            left_motor: Left side drive motor(s) - can be Motor or MotorGroup
            right_motor: Right side drive motor(s) - can be Motor or MotorGroup  
            strafe_motor: Strafing motor(s) - can be Motor or MotorGroup
            inertia_sensor: Inertial sensor for heading tracking
        """
        self.left_motor = left_motor
        self.right_motor = right_motor
        self.strafe_motor = strafe_motor
        self.inertia_sensor = inertia_sensor

        # Movement Override. When True, manual control should NOT be applied.
        self.movement_override = False

    def drive(self, forward, strafe, turn):
        """
        Drive the robot using arcade-style controls
        
        Args:
            forward: Forward/backward speed (-100 to 100)
            strafe: Left/right strafe speed (-100 to 100)
            turn: Turn speed (-100 to 100)
        """
        left_speed = forward + turn
        right_speed = forward - turn
        strafe_speed = strafe

        self.left_motor.spin(FORWARD, left_speed, PERCENT)
        self.right_motor.spin(FORWARD, right_speed, PERCENT)
        self.strafe_motor.spin(FORWARD, strafe_speed, PERCENT)

    def drive_for_blind(self, forward, right, speed=100, brake_type=BRAKE):
        """
        Drive the robot for a specific distance using arcade-style controls.
        This method does not use feedback from the inertial sensor, and is thus "blind".
        Units: millimeters (MM)
        
        Args:
            forward: Forward/backward distance in millimeters (MM)
            right: Left/right strafe distance in millimeters (MM). Positive is right, negative is left.
            speed: Speed percentage (0 to 100)
            brake_type: Type of braking to apply at the end of movement (BRAKE, COAST, or HOLD)
        """
        self.movement_override = True

        drivetrain.stop()

        left_distance = forward
        right_distance = forward
        strafe_distance = right

        # Perform calculation to figure out how many revolutions each motor needs to turn
        left_motor_rotations = left_distance / (3.14159 * self.left_motor.wheel_diameter_mm) * 360
        right_motor_rotations = right_distance / (3.14159 * self.right_motor.wheel_diameter_mm) * 360
        strafe_motor_rotations = strafe_distance / (3.14159 * self.strafe_motor.wheel_diameter_mm) * 360

        # Store current braking mode and set to BRAKE for precise stopping
        current_braking_mode = RobotState.current_braking_mode
        self.set_stopping_mode(brake_type)

        # Store current motor speeds
        left_motor_speed = self.left_motor.velocity(PERCENT)
        right_motor_speed = self.right_motor.velocity(PERCENT)
        strafe_motor_speed = self.strafe_motor.velocity(PERCENT)

        # Update motor speeds to 100% for driving
        self.left_motor.set_velocity(speed, PERCENT)
        self.right_motor.set_velocity(speed, PERCENT)
        self.strafe_motor.set_velocity(speed, PERCENT)

        self.left_motor.spin_for(FORWARD, left_motor_rotations, DEGREES, wait=False)
        self.right_motor.spin_for(FORWARD, right_motor_rotations, DEGREES, wait=False)
        self.strafe_motor.spin_for(FORWARD, strafe_motor_rotations, DEGREES, wait=False)
        
        # Wait for motors to stop spinning
        timer = Timer()
        while (self.left_motor.is_spinning() or self.right_motor.is_spinning() or self.strafe_motor.is_spinning()) \
            and timer.time() < 5000: # 5 second timeout
            wait(10, MSEC)

        # Restore previous braking mode
        self.set_stopping_mode(current_braking_mode)

        # Restore previous motor speeds
        self.left_motor.set_velocity(left_motor_speed, PERCENT)
        self.right_motor.set_velocity(right_motor_speed, PERCENT)
        self.strafe_motor.set_velocity(strafe_motor_speed, PERCENT)

        self.movement_override = False

    def turn_for(self, angle_degrees, speed=50, timeout_ms=5000):
        """
        Turn the robot for a specific angle using the inertial sensor.
        This method uses feedback from the inertial sensor to achieve accurate turns.
        Args:
            angle_degrees: Angle to turn in degrees (positive for clockwise, negative for counter-clockwise)
            speed: Speed percentage (0 to 100)
            timeout_ms: Maximum time to wait for turn completion in milliseconds (default 5000ms)
        """
        self.movement_override = True
        drivetrain.stop()
        
        # Store current braking mode and set to BRAKE for precise stopping
        current_braking_mode = RobotState.current_braking_mode
        self.set_stopping_mode(BRAKE)
        
        # Calculate headings
        initial_heading = self.inertia_sensor.heading()
        target_heading = (initial_heading + angle_degrees) % 360
        heading_difference = self._normalize_angle_difference(target_heading - initial_heading)
        
        # Turn based on shortest path
        if heading_difference > 0:
            # Turn clockwise
            self.left_motor.spin(FORWARD, speed, PERCENT)
            self.right_motor.spin(REVERSE, speed, PERCENT)
        else:
            # Turn counter-clockwise
            self.left_motor.spin(REVERSE, speed, PERCENT)
            self.right_motor.spin(FORWARD, speed, PERCENT)
        
        # Start timeout timer
        start_time = brain.timer.time(MSEC)
        
        # Continue turning until target heading is reached or timeout
        while brain.timer.time(MSEC) - start_time < timeout_ms:
            current_heading = self.inertia_sensor.heading()
            heading_difference = self._normalize_angle_difference(target_heading - current_heading)
            
            # Stop if within tolerance
            if abs(heading_difference) < 1.0:
                break
            
            wait(10, MSEC)
        else:
            logger.warning("Turn timed out before reaching target heading")
        
        # Stop motors
        self.stop()
        
        # Restore previous braking mode
        self.set_stopping_mode(current_braking_mode)
        self.movement_override = False

    def stop(self, brake_type=BRAKE):
        """
        Stop all drivetrain motors
        
        Args:
            brake_type: Type of braking to apply (BRAKE, COAST, or HOLD)
        """
        self.left_motor.stop(brake_type)
        self.right_motor.stop(brake_type)
        self.strafe_motor.stop(brake_type)

    def set_stopping_mode(self, brake_type):
        """
        Set the stopping mode for all drivetrain motors
        
        Args:
            brake_type: Type of braking to apply (BRAKE, COAST, or HOLD)
        """
        self.left_motor.set_stopping(brake_type)
        self.right_motor.set_stopping(brake_type)
        self.strafe_motor.set_stopping(brake_type)
    
    def set_velocity(self, velocity, units=PERCENT):
        """
        Set the default velocity for all drivetrain motors
        
        Args:
            velocity: Velocity value
            units: Velocity units (PERCENT, RPM, etc.)
        """
        self.left_motor.set_velocity(velocity, units)
        self.right_motor.set_velocity(velocity, units)
        self.strafe_motor.set_velocity(velocity, units)

    def _normalize_angle_difference(self, angle_difference):
        """Normalize angle difference to range [-180, 180] degrees"""
        while angle_difference > 180:
            angle_difference -= 360
        while angle_difference < -180:
            angle_difference += 360
        return angle_difference



# =============================================================================
# ROBOT CONFIGURATION
# =============================================================================

brain = Brain()
controller = CustomController()

class Wheels:
    class Diameters:
        DRIVE_WHEEL_DIAMETER_MM = 105  # Diameter of the drive wheels in millimeters
        STRAFE_WHEEL_DIAMETER_MM = 105   # Diameter of the strafing wheel in millimeters

class Motors:
    # Individual drive motors
    left_front_motor = WheelMotor(Ports.PORT7, GearSetting.RATIO_18_1, False, Wheels.Diameters.DRIVE_WHEEL_DIAMETER_MM)
    left_back_motor = WheelMotor(Ports.PORT10, GearSetting.RATIO_18_1, False, Wheels.Diameters.DRIVE_WHEEL_DIAMETER_MM)
    right_front_motor = WheelMotor(Ports.PORT9, GearSetting.RATIO_18_1, True, Wheels.Diameters.DRIVE_WHEEL_DIAMETER_MM)
    right_back_motor = WheelMotor(Ports.PORT8, GearSetting.RATIO_18_1, True, Wheels.Diameters.DRIVE_WHEEL_DIAMETER_MM)

    # Strafing motor
    strafe_motor = WheelMotor(Ports.PORT11, GearSetting.RATIO_18_1, False, Wheels.Diameters.STRAFE_WHEEL_DIAMETER_MM)
    
    # Motor groups for efficient control
    left_motor_group = WheelMotorGroup(left_front_motor, left_back_motor)
    right_motor_group = WheelMotorGroup(right_front_motor, right_back_motor)

    # Intake
    bottom_intake_motor = Motor(Ports.PORT6, GearSetting.RATIO_18_1, False)
    top_intake_motor = Motor(Ports.PORT20, GearSetting.RATIO_18_1, True)
    unloading_motor = Motor(Ports.PORT19, GearSetting.RATIO_18_1, True)

class Solenoids:
    intake_solenoid = Pneumatics(brain.three_wire_port.h)
    descorer_solenoid = Pneumatics(brain.three_wire_port.f)
    match_load_unloader_solenoid = Pneumatics(brain.three_wire_port.d)

class Sensors:
    inertia_sensor = Inertial(Ports.PORT18)
    intake_optical_sensor_right = Optical(Ports.PORT5)
    intake_optical_sensor_left = Optical(Ports.PORT4)

    @classmethod
    def initialize_sensors(cls):
        """Initialize sensors"""
        # Set light power for optical sensors
        cls.intake_optical_sensor_left.set_light_power(100)
        cls.intake_optical_sensor_right.set_light_power(100)

        # Set detection distance for optical sensors
        cls.intake_optical_sensor_left.object_detect_threshold(40)
        cls.intake_optical_sensor_right.object_detect_threshold(40)

        # Calibrate inertial sensor
        logger.info("Calibrating inertial sensor...")
        cls.inertia_sensor.calibrate()
        logger.info("Inertial sensor calibration complete.")

Sensors.initialize_sensors()

# Create logger instance (requires brain and controller to be initialized)
logger = Logger(brain, controller)

# Drivetrain instance using motor groups
drivetrain = Drivetrain(Motors.left_motor_group, Motors.right_motor_group, Motors.strafe_motor, Sensors.inertia_sensor)



# =============================================================================
# BLOCK MANIPULATION SYSTEMS
# =============================================================================

class BlockManipulationSystem:
    def __init__(self):
        self._state = BlockManipulationSystem.State.IDLE
        self._intaking = self._Intaking()
        self._outputting = self._Outputting()

    class State:
        IDLE = 0
        INTAKING = 1
        OUTPUTTING_LOW = 2
        OUTPUTTING_MEDIUM = 3
        OUTPUTTING_HIGH = 4

    def set_state(self, new_state):
        self._state = new_state

    def set_and_update_state(self, new_state):
        self.set_state(new_state)
        self.update()

    def update(self):
        """Main tick function to update the system based on current state"""
        if self._state == BlockManipulationSystem.State.INTAKING:
            self._intaking.handle_intaking()
        elif self._state == BlockManipulationSystem.State.OUTPUTTING_LOW:
            self._outputting.handle_output_low()
        elif self._state == BlockManipulationSystem.State.OUTPUTTING_MEDIUM:
            self._outputting.handle_output_medium()
        elif self._state == BlockManipulationSystem.State.OUTPUTTING_HIGH:
            self._outputting.handle_output_high()
        else:
            self._handle_idle()

    class _Intaking:
        reject_current_block = False
        last_trigger_time = 0
        def handle_intaking(self):
            """Intaking logic"""
            self._check_current_block()
            Solenoids.intake_solenoid.open()  # Expand/extend the intake
            Motors.bottom_intake_motor.spin(FORWARD, 100, PERCENT)
            Motors.top_intake_motor.spin(FORWARD if not self.reject_current_block else REVERSE, 100, PERCENT)
            Motors.unloading_motor.stop(BRAKE)

        def _check_current_block(self):
            """Check if the current block should be rejected based on vision sensor"""     
            def classify_color(hue):
                if 0 <= hue <= 10:
                    return AllianceColor("red")
                elif 80 <= hue <= 255:
                    return AllianceColor("blue")
                else:
                    return AllianceColor("unknown")
                
            # Check that system is active (alliance color is known)
            if RobotState.current_alliance_color == AllianceColor("unknown"):
                self.reject_current_block = False
                return

            # Turn on intake color sensor lights
            Sensors.intake_optical_sensor_left.set_light(LedStateType.ON)
            Sensors.intake_optical_sensor_right.set_light(LedStateType.ON)

            # Get current object from vision sensor
            left_hue = classify_color(Sensors.intake_optical_sensor_left.hue())
            right_hue = classify_color(Sensors.intake_optical_sensor_right.hue())

            # logger.info("Color: Left Hue: " + str(Sensors.intake_optical_sensor_left.hue()), ScreenTarget.BRAIN)

            if Sensors.intake_optical_sensor_right.is_near_object() or Sensors.intake_optical_sensor_left.is_near_object():
                # Red object detection
                if left_hue == AllianceColor("red") or right_hue == AllianceColor("red"):
                    self.reject_current_block = (RobotState.current_alliance_color != AllianceColor("red"))
                    self.last_trigger_time = brain.timer.time()
                    logger.debug("Red block detected - accepting", ScreenTarget.BOTH)
                    return

                # Blue object detection
                if left_hue == AllianceColor("blue") or right_hue == AllianceColor("blue"):
                    self.reject_current_block = (RobotState.current_alliance_color != AllianceColor("blue"))
                    self.last_trigger_time = brain.timer.time()
                    logger.debug("Blue block detected - rejecting", ScreenTarget.BOTH)
                    return
                
            TIME_DELAY_IN_MILLISECONDS = 1000
            if self.reject_current_block and ((brain.timer.time() - self.last_trigger_time) > TIME_DELAY_IN_MILLISECONDS):
                self.reject_current_block = False
                logger.debug("No block detected - accepting by default", ScreenTarget.BOTH)

    class _Outputting:
        def handle_output_low(self):
            """Output low logic"""
            Motors.bottom_intake_motor.spin(REVERSE, 100, PERCENT)
            Motors.top_intake_motor.stop(BRAKE)
            Motors.unloading_motor.spin(REVERSE, 100, PERCENT)

        def handle_output_medium(self):
            """Output medium logic"""
            Motors.bottom_intake_motor.spin(FORWARD, 100, PERCENT)
            Motors.top_intake_motor.spin(REVERSE, 100, PERCENT)
            Motors.unloading_motor.spin(REVERSE, 100, PERCENT)

        def handle_output_high(self):
            """Output high logic"""
            Solenoids.intake_solenoid.close()  # Retract/contract the intake
            Motors.bottom_intake_motor.spin(FORWARD, 100, PERCENT)
            Motors.top_intake_motor.spin(FORWARD, 100, PERCENT)
            Motors.unloading_motor.spin(REVERSE, 100, PERCENT)
    
    def _handle_idle(self):
        """Idle state - stop all motors"""
        Motors.bottom_intake_motor.stop(BRAKE)
        Motors.top_intake_motor.stop(BRAKE)
        Motors.unloading_motor.stop(BRAKE)

        # Ensure intake color sensor lights are off
        Sensors.intake_optical_sensor_left.set_light(LedStateType.OFF)
        Sensors.intake_optical_sensor_right.set_light(LedStateType.OFF)

block_manipulation_system = BlockManipulationSystem()



# =============================================================================
# GAME MODES
# =============================================================================

class Autonomous:
    @classmethod
    def start(cls):
        """Start autonomous mode code. This function should not return."""
        logger.info("=== AUTONOMOUS MODE STARTED ===")

        try:
            # Example autonomous routine with logging
            logger.info("Starting autonomous routine")

            current_alliance_color = RobotState.current_alliance_color = AllianceColor("unknown")  # Set to unknown to disable color-based rejection

            if RobotState.starting_side == "RIGHT":
                cls.run_right_side_routine()
            else:
                cls.run_left_side_routine()

            RobotState.current_alliance_color = current_alliance_color  # Restore alliance color

            logger.info("Autonomous routine completed successfully")

        except Exception as e:
            logger.error("Autonomous routine failed: " + str(e))
            logger.error("Emergency stop activated")
        logger.info("=== AUTONOMOUS MODE ENDED ===")

    @staticmethod
    def run_right_side_routine():
        """Run autonomous routine for right side starting position"""
        # Move to blocks
        drivetrain.drive_for_blind(580, 150, 50)
        
        # Pick up blocks
        block_manipulation_system.set_and_update_state(BlockManipulationSystem.State.INTAKING)
        wait(100, MSEC)  # Simulate time taken to intake blocks
        drivetrain.drive_for_blind(630, 0, 10)
        wait(2000, MSEC)  # Wait for capture system
        block_manipulation_system.set_and_update_state(BlockManipulationSystem.State.IDLE)

        # Reorient towards goal
        drivetrain.turn_for(-45, 50)
        drivetrain.drive_for_blind(230, 0, 50)
        # drivetrain.drive_for_blind(-10, -50, 50)

        # Score blocks
        block_manipulation_system.set_and_update_state(BlockManipulationSystem.State.OUTPUTTING_LOW)
        wait(5000, MSEC)  # Simulate time taken to output blocks
        block_manipulation_system.set_and_update_state(BlockManipulationSystem.State.IDLE)

        # for _ in range(3):
        #     block_manipulation_system.set_and_update_state(BlockManipulationSystem.State.OUTPUTTING_LOW)
        #     wait(1000, MSEC)
        #     block_manipulation_system.set_and_update_state(BlockManipulationSystem.State.IDLE)

        #     wait(500, MSEC)
            
        #     drivetrain.drive_for_blind(-100, 0, 100)
        #     for _ in range(3):
        #         # Shake
        #         drivetrain.drive_for_blind(50, 0, 100)
        #         drivetrain.drive_for_blind(-50, 0, 100)

        #     wait(100, MSEC)
        #     drivetrain.drive_for_blind(100, 0, 100)

    @staticmethod
    def run_left_side_routine():
        """Run autonomous routine for left side starting position"""
        # Move to blocks
        drivetrain.drive_for_blind(580, -150, 50)
        
        # Pick up blocks
        block_manipulation_system.set_and_update_state(BlockManipulationSystem.State.INTAKING)
        wait(100, MSEC)  # Simulate time taken to intake blocks
        drivetrain.drive_for_blind(630, 0, 10)
        wait(2000, MSEC)  # Wait for capture system
        block_manipulation_system.set_and_update_state(BlockManipulationSystem.State.IDLE)

        # Reorient towards goal
        drivetrain.turn_for(45, 50)
        drivetrain.drive_for_blind(240, 0, 50)
        # drivetrain.drive_for_blind(0, 100, 50)

        # Score blocks
        block_manipulation_system.set_and_update_state(BlockManipulationSystem.State.OUTPUTTING_MEDIUM)
        wait(5000, MSEC)  # Simulate time taken to output blocks
        block_manipulation_system.set_and_update_state(BlockManipulationSystem.State.IDLE)

class DriverControl:
    running = False
    _last_input_log_time = 0

    @classmethod
    def start(cls):
        """Start driver control mode code. This function should not return."""
        logger.info("=== DRIVER CONTROL MODE STARTED ===", ScreenTarget.BOTH)

        # Register callbacks for buttons
        cls._register_button_callbacks()

        # Start main driver control loop
        cls.running = True

        try:
            drivetrain.set_stopping_mode(RobotState.current_braking_mode)

            while cls.running:
                cls._update_drivetrain()
                cls._update_block_manipulation_systems_state()
                wait(20, MSEC) # Run the loop every 20 milliseconds (50 times per second)

        except Exception as e:
            logger.critical("Driver control crashed: " + str(e))
            logger.critical("Robot stopped for safety", ScreenTarget.BOTH)
            logger.error("Restarting driver control mode...", ScreenTarget.BOTH)
            cls.start()  # Restart driver control mode

    @classmethod
    def _register_button_callbacks(cls):
        """Register button callbacks for driver control mode"""
        
        # Configuration
        controller.get_button(ControllerSettings.COLOR_SWITCH_BUTTON).pressed(cls.switch_alliance_color)

        # Driving
        controller.get_button(ControllerSettings.BRAKING_SWITCH_BUTTON).pressed(cls.switch_braking_mode) 
        controller.get_button(ControllerSettings.FC_FORWARD_BUTTON).pressed(lambda: drivetrain.drive_for_blind(100, 0))
        controller.get_button(ControllerSettings.FC_BACKWARD_BUTTON).pressed(lambda: drivetrain.drive_for_blind(-100, 0))
        
        # Features
        controller.get_button(ControllerSettings.DESCORER_TRIGGER_BUTTON).pressed(cls.trigger_descorer)
        controller.get_button(ControllerSettings.MATCH_LOAD_UNLOADER_TOGGLE_BUTTON).pressed(cls.toggle_match_load_unloader)

    @classmethod
    def _update_drivetrain(cls):
        """To be called repeatedly in driver control mode to update the drivetrain"""

        if drivetrain.movement_override:
            return  # Skip manual control if movement override is active
        
        # Get joystick values with deadzone applied
        forward = controller.get_axis_with_deadzone(ControllerSettings.FORWARD_BACKWARD_AXIS)
        turn = controller.get_axis_with_deadzone(ControllerSettings.TURN_AXIS)
        strafe = controller.get_button(ControllerSettings.STRAFE_RIGHT_BUTTON).pressing() * 100 - \
                controller.get_button(ControllerSettings.STRAFE_LEFT_BUTTON).pressing() * 100  

        # Log significant inputs occasionally (not every loop to avoid spam)
        current_time = brain.timer.time()
        if (abs(forward) > 50 or abs(strafe) > 50 or abs(turn) > 50) and \
        (current_time - cls._last_input_log_time > 2000):  # Log every 2 seconds max
            debug_msg = "Driver input: F:" + str(int(forward)) + " S:" + str(int(strafe)) + " T:" + str(int(turn))
            logger.debug(debug_msg, ScreenTarget.BRAIN)
            cls._last_input_log_time = current_time

        # Apply speed modifiers
        forward *= DrivetrainSettings.FORWARD_BACKWARD_SPEED_MODIFIER
        strafe *= DrivetrainSettings.STRAFE_SPEED_MODIFIER
        turn *= DrivetrainSettings.TURN_SPEED_MODIFIER

        # Command the drivetrain to move
        try:
            drivetrain.drive(forward, strafe, turn)
        except Exception as e:
            logger.error("Drivetrain command failed: " + str(e))

    @staticmethod
    def _update_block_manipulation_systems_state():
        """To be called repeatedly in driver control mode to update the block manipulation systems"""
        if controller.get_button(ControllerSettings.INTAKE_BUTTON).pressing(): # Intake
            block_manipulation_system.set_state(BlockManipulationSystem.State.INTAKING)
        elif controller.get_button(ControllerSettings.OUTPUT_LOW_BUTTON).pressing(): # Output low
            block_manipulation_system.set_state(BlockManipulationSystem.State.OUTPUTTING_LOW)
        elif controller.get_button(ControllerSettings.OUTPUT_MEDIUM_BUTTON).pressing(): # Output medium
            block_manipulation_system.set_state(BlockManipulationSystem.State.OUTPUTTING_MEDIUM)
        elif controller.get_button(ControllerSettings.OUTPUT_HIGH_BUTTON).pressing(): # Output high
            block_manipulation_system.set_state(BlockManipulationSystem.State.OUTPUTTING_HIGH)
        else:
            block_manipulation_system.set_state(BlockManipulationSystem.State.IDLE)

        block_manipulation_system.update()

    @staticmethod
    def change_starting_side(value):
        """Change the starting side of the robot"""
        RobotState.starting_side.set(value)
        logger.info("Starting side set to " + str(RobotState.starting_side), ScreenTarget.BRAIN)
        logger.info("Starting side: " + str(RobotState.starting_side), ScreenTarget.CONTROLLER)

    @staticmethod
    def switch_alliance_color():
        """Switch the current alliance color"""
        LONG_PRESS_THRESHOLD_MS = 1000  # 1 second threshold for long press

        # Define color if not defined already
        if RobotState.current_alliance_color == AllianceColor("unknown"):
            RobotState.current_alliance_color.set_to_default()
        
        # Toggle Color
        RobotState.current_alliance_color = ~RobotState.current_alliance_color

        logger.info("Alliance color switched to " + str(RobotState.current_alliance_color), ScreenTarget.BRAIN)
        logger.info(str(RobotState.current_alliance_color) + " alliance selected", ScreenTarget.CONTROLLER)

        # =============================== LONG PRESS FUNCTIONALITY ========================================
        init_time = brain.timer.time()
        while controller.get_button(ControllerSettings.COLOR_SWITCH_BUTTON).pressing():
            wait(10, MSEC)
            if brain.timer.time() - init_time > LONG_PRESS_THRESHOLD_MS:  # Early exit for long press
                break

        if brain.timer.time() - init_time > LONG_PRESS_THRESHOLD_MS:  # Long press detected
            RobotState.current_alliance_color = AllianceColor("unknown")
            logger.warning("Alliance color switched to UNKNOWN; color detection disabled.", ScreenTarget.BRAIN)
            logger.warning("Color detection disabled.", ScreenTarget.CONTROLLER)
        
    @staticmethod
    def switch_braking_mode():
        """Switch the drivetrain braking mode between BRAKE and COAST"""
        if RobotState.current_braking_mode == BRAKE:
            new_mode = COAST
        else:
            new_mode = BRAKE

        RobotState.current_braking_mode = new_mode
        drivetrain.set_stopping_mode(new_mode)

        str_name = "BRAKE" if new_mode == BRAKE else "COAST"

        logger.info("Drivetrain braking mode switched to " + str_name, ScreenTarget.BRAIN)
        logger.info(str_name + " braking mode.", ScreenTarget.CONTROLLER)

    @classmethod
    def trigger_descorer(cls):
        """Trigger the descorer solenoid in a separate thread."""
        cls._TriggerDescorer()
    class _TriggerDescorer:
        def __init__(self):
            """Trigger the descorer solenoid in a separate thread."""
            Thread(self._trigger_descorer_thread)

        def _trigger_descorer_thread(self):
            """Trigger the descorer solenoid. This function is blocking, so it should be run in a separate thread."""
            Solenoids.descorer_solenoid.open()
            logger.debug("Descorer triggered", ScreenTarget.BOTH)
            wait(500, MSEC)  # Keep descorer active for 500 milliseconds
            Solenoids.descorer_solenoid.close()

    @staticmethod
    def toggle_match_load_unloader():
        """Toggle the match load unloader motor"""
        if Solenoids.match_load_unloader_solenoid.value():
            Solenoids.match_load_unloader_solenoid.close()
            logger.info("Match load unloader retracted", ScreenTarget.BOTH)
        else:
            Solenoids.match_load_unloader_solenoid.open()
            logger.info("Match load unloader deployed", ScreenTarget.BOTH)


# =============================================================================
# CONFIGURATION SCREENS
# =============================================================================

class ConfigurationScreen:
    """Dynamic tabbed configuration screen for pre-autonomous setup"""

    TABS = []
    
    # Screen dimensions
    SCREEN_WIDTH = 480
    SCREEN_HEIGHT = 272
    TAB_HEIGHT = 40
    DONE_BUTTON_HEIGHT = 50
    
    def __init__(self, brain_instance: Brain, logger_instance, competition_instance):
        self.brain = brain_instance
        self.logger = logger_instance
        self.comp = competition_instance
        
        self.current_tab = 0
        self.selection_complete = False
        self.last_touch_time = 0
        self.thread_running = True
        
        # Store previous alliance color for toggle feature
        self.previous_alliance_color = RobotState.current_alliance_color
        
        # Set tabs
        self.TABS.append({"name": "Main Settings", "draw_func": self._draw_main_settings_tab})
        self.TABS.append({"name": "Other Configs", "draw_func": self._draw_other_configs_tab})
    
    def _calculate_tab_dimensions(self):
        """Calculate tab button dimensions based on number of tabs"""
        num_tabs = len(self.TABS)
        tab_width = self.SCREEN_WIDTH // num_tabs
        return tab_width, self.TAB_HEIGHT
    
    def _draw_tabs(self):
        """Draw the tab bar at the top"""
        tab_width, tab_height = self._calculate_tab_dimensions()
        
        for i, tab in enumerate(self.TABS):
            x = i * tab_width
            
            # Set color based on whether this is the active tab
            if i == self.current_tab:
                self.brain.screen.set_fill_color(Color.WHITE)
                self.brain.screen.set_pen_color(Color.BLACK)
            else:
                self.brain.screen.set_fill_color(Color.BLACK)
                self.brain.screen.set_pen_color(Color.WHITE)
            
            # Draw tab rectangle
            self.brain.screen.draw_rectangle(x, 0, tab_width, tab_height)
            
            # Draw tab name (center it)
            # Calculate approximate column position
            text_col = (x + tab_width // 2) // 10 - len(tab["name"]) // 2
            self.brain.screen.set_cursor(2, max(1, text_col))
            self.brain.screen.print(tab["name"])
    
    def _draw_done_button(self):
        """Draw the Done button at the bottom of the screen"""
        button_y = self.SCREEN_HEIGHT - self.DONE_BUTTON_HEIGHT - 5
        button_width = 200
        button_x = (self.SCREEN_WIDTH - button_width) // 2
        
        self.brain.screen.set_fill_color(Color.PURPLE)
        self.brain.screen.set_pen_color(Color.WHITE)
        self.brain.screen.draw_rectangle(button_x, button_y, button_width, self.DONE_BUTTON_HEIGHT)
        self.brain.screen.set_cursor(30, 20)
        self.brain.screen.print("DONE")
    
    def _draw_main_settings_tab(self):
        """Draw the Main Settings tab content"""
        content_y = self.TAB_HEIGHT + 10
        button_height = 70
        button_spacing = 10
        button_width = (self.SCREEN_WIDTH - 30) // 2
        
        # Title
        self.brain.screen.set_pen_color(Color.WHITE)
        self.brain.screen.set_cursor(5, 15)
        self.brain.screen.print("Starting Side")
        
        # Side selection buttons (top row)
        # LEFT button
        if RobotState.starting_side == "LEFT":
            self.brain.screen.set_fill_color(Color.GREEN)
        else:
            self.brain.screen.set_fill_color(Color.TRANSPARENT)
        self.brain.screen.draw_rectangle(10, content_y, button_width, button_height)
        self.brain.screen.set_cursor(8, 8)
        self.brain.screen.print("LEFT")
        
        # RIGHT button
        if RobotState.starting_side == "RIGHT":
            self.brain.screen.set_fill_color(Color.GREEN)
        else:
            self.brain.screen.set_fill_color(Color.TRANSPARENT)
        self.brain.screen.draw_rectangle(10 + button_width + button_spacing, content_y, button_width, button_height)
        self.brain.screen.set_cursor(8, 33)
        self.brain.screen.print("RIGHT")
        
        # Alliance color title
        content_y += button_height + button_spacing
        self.brain.screen.set_cursor(11, 13)
        self.brain.screen.print("Alliance Color")
        
        # Alliance color buttons (bottom row)
        content_y += 20
        
        # BLUE button
        if str(RobotState.current_alliance_color) == "BLUE":
            self.brain.screen.set_fill_color(Color.BLUE)
        else:
            self.brain.screen.set_fill_color(Color.TRANSPARENT)
        self.brain.screen.draw_rectangle(10, content_y, button_width, button_height)
        self.brain.screen.set_cursor(14, 8)
        self.brain.screen.print("BLUE")
        
        # RED button
        if str(RobotState.current_alliance_color) == "RED":
            self.brain.screen.set_fill_color(Color.RED)
        else:
            self.brain.screen.set_fill_color(Color.TRANSPARENT)
        self.brain.screen.draw_rectangle(10 + button_width + button_spacing, content_y, button_width, button_height)
        self.brain.screen.set_cursor(14, 34)
        self.brain.screen.print("RED")
    
    def _draw_other_configs_tab(self):
        """Draw the Other Configs tab content"""
        content_y = self.TAB_HEIGHT + 10
        button_height = 55
        button_spacing = 10
        button_width = (self.SCREEN_WIDTH - 40) // 3
        
        # Braking mode section
        self.brain.screen.set_pen_color(Color.WHITE)
        self.brain.screen.set_cursor(5, 13)
        self.brain.screen.print("Braking Mode")
        
        # Braking mode buttons
        modes = [(COAST, "COAST", 6), (BRAKE, "BRAKE", 18), (HOLD, "HOLD", 31)]
        for i, (mode, name, col) in enumerate(modes):
            x = 10 + i * (button_width + button_spacing)
            
            if RobotState.current_braking_mode == mode:
                self.brain.screen.set_fill_color(Color.ORANGE)
            else:
                self.brain.screen.set_fill_color(Color.TRANSPARENT)
            
            self.brain.screen.draw_rectangle(x, content_y, button_width, button_height)
            self.brain.screen.set_cursor(8, col)
            self.brain.screen.print(name)
        
        # Color detection toggle section
        content_y += button_height + button_spacing + 20
        self.brain.screen.set_cursor(11, 10)
        self.brain.screen.print("Color Detection")
        
        content_y += 20
        
        # Toggle button
        is_enabled = str(RobotState.current_alliance_color) != "UNKNOWN"
        
        if is_enabled:
            self.brain.screen.set_fill_color(Color.GREEN)
            label = "ENABLED"
            col = 15
        else:
            self.brain.screen.set_fill_color(Color.RED)
            label = "DISABLED"
            col = 13
        
        toggle_width = 200
        toggle_x = (self.SCREEN_WIDTH - toggle_width) // 2
        self.brain.screen.draw_rectangle(toggle_x, content_y, toggle_width, button_height)
        self.brain.screen.set_cursor(15, col)
        self.brain.screen.print(label)
    
    def _check_done_button_press(self, x, y):
        """Check if the Done button was pressed"""
        button_y = self.SCREEN_HEIGHT - self.DONE_BUTTON_HEIGHT - 5
        button_width = 200
        button_x = (self.SCREEN_WIDTH - button_width) // 2
        
        if button_y <= y <= button_y + self.DONE_BUTTON_HEIGHT:
            if button_x <= x <= button_x + button_width:
                return True
        return False
    
    def _handle_main_settings_press(self, x, y):
        """Handle touch input for Main Settings tab"""
        content_y = self.TAB_HEIGHT + 10
        button_height = 70
        button_spacing = 10
        button_width = (self.SCREEN_WIDTH - 30) // 2
        
        # Check side selection (top row)
        if content_y <= y <= content_y + button_height:
            if 10 <= x <= 10 + button_width:
                # LEFT button
                RobotState.starting_side = Side("LEFT")
                return True
            elif 10 + button_width + button_spacing <= x <= self.SCREEN_WIDTH - 10:
                # RIGHT button
                RobotState.starting_side = Side("RIGHT")
                return True
        
        # Check alliance color selection (bottom row)
        content_y += button_height + button_spacing + 20
        if content_y <= y <= content_y + button_height:
            if 10 <= x <= 10 + button_width:
                # BLUE button
                RobotState.current_alliance_color = AllianceColor("BLUE")
                self.previous_alliance_color = RobotState.current_alliance_color
                return True
            elif 10 + button_width + button_spacing <= x <= self.SCREEN_WIDTH - 10:
                # RED button
                RobotState.current_alliance_color = AllianceColor("RED")
                self.previous_alliance_color = RobotState.current_alliance_color
                return True
        
        return False
    
    def _handle_other_configs_press(self, x, y):
        """Handle touch input for Other Configs tab"""
        content_y = self.TAB_HEIGHT + 10
        button_height = 55
        button_spacing = 10
        button_width = (self.SCREEN_WIDTH - 40) // 3
        
        # Check braking mode buttons
        if content_y <= y <= content_y + button_height:
            modes = [COAST, BRAKE, HOLD]
            for i, mode in enumerate(modes):
                button_x = 10 + i * (button_width + button_spacing)
                if button_x <= x <= button_x + button_width:
                    RobotState.current_braking_mode = mode
                    return True
        
        # Check color detection toggle
        content_y += button_height + button_spacing + 20 + 20
        toggle_width = 200
        toggle_x = (self.SCREEN_WIDTH - toggle_width) // 2
        
        if content_y <= y <= content_y + button_height:
            if toggle_x <= x <= toggle_x + toggle_width:
                # Toggle color detection
                if str(RobotState.current_alliance_color) == "UNKNOWN":
                    # Re-enable: restore previous color
                    RobotState.current_alliance_color = self.previous_alliance_color
                else:
                    # Disable: set to UNKNOWN
                    self.previous_alliance_color = RobotState.current_alliance_color
                    RobotState.current_alliance_color = AllianceColor("UNKNOWN")
                return True
        
        return False
    
    def _check_touch_input(self):
        """Check for touch input and handle accordingly"""
        if not self.brain.screen.pressing():
            return False
        
        x = self.brain.screen.x_position()
        y = self.brain.screen.y_position()
        
        # Update last touch time
        self.last_touch_time = brain.timer.time(SECONDS)
        
        # Check if clicking Done button
        if self._check_done_button_press(x, y):
            self.selection_complete = True
            # Wait for release to prevent multiple triggers
            while self.brain.screen.pressing():
                wait(20, MSEC)
            return True
        
        # Check if clicking on tabs
        tab_width, tab_height = self._calculate_tab_dimensions()
        if y <= tab_height:
            # Clicking on tab bar
            tab_index = x // tab_width
            if 0 <= tab_index < len(self.TABS):
                if tab_index != self.current_tab:
                    self.current_tab = tab_index
                    self._draw_screen()
            return False
        
        # Handle press in current tab's content area
        redraw_needed = False
        if self.current_tab == 0:
            redraw_needed = self._handle_main_settings_press(x, y)
        elif self.current_tab == 1:
            redraw_needed = self._handle_other_configs_press(x, y)
        
        if redraw_needed:
            self._draw_screen()
            # Wait for release to prevent multiple triggers
            while self.brain.screen.pressing():
                wait(20, MSEC)
        
        return False
    
    def _draw_screen(self):
        """Draw the complete screen with tabs and current content"""
        self.brain.screen.clear_screen()
        self.brain.screen.set_pen_width(2)
        
        # Draw tabs
        self._draw_tabs()
        
        # Draw current tab content
        if self.TABS[self.current_tab]["draw_func"]:
            self.TABS[self.current_tab]["draw_func"]()
        
        # Draw Done button
        self._draw_done_button()
    
    def _should_exit(self):
        """Check if we should exit the configuration screen"""
        # Exit if Done button was pressed
        if self.selection_complete:
            return True
        
        # Check if competition mode has started
        mode_started = self.comp.is_autonomous() or self.comp.is_driver_control()
        
        if mode_started:
            # If mode started, check 5 second timeout since last touch
            current_time = brain.timer.time(SECONDS)
            time_since_touch = current_time - self.last_touch_time
            
            if time_since_touch >= 5.0:
                return True
        
        return False
    
    def _run_thread(self):
        """Main thread function for the configuration screen"""
        # Disable brain logging while config screen is active
        self.logger.brain_logging_enabled = False
        
        # Draw initial screen
        self._draw_screen()
        
        # Initialize last touch time
        self.last_touch_time = brain.timer.time(SECONDS)
        
        # Log to controller only
        self.logger.info("Configuration screen active", ScreenTarget.CONTROLLER)
        
        # Keep the screen interactive
        while self.thread_running:
            if self._check_touch_input():
                # Done button was pressed
                break
            
            if self._should_exit():
                break
            
            wait(50, MSEC)
        
        # Re-enable brain logging
        self.logger.brain_logging_enabled = True
        
        # Clear screen and log final settings
        self.brain.screen.clear_screen()
        self.logger.info("Config complete - Side: " + str(RobotState.starting_side) + " Color: " + str(RobotState.current_alliance_color))
        
        self.thread_running = False
    
    def run(self):
        """Run the configuration screen in a separate thread"""
        # Create and start thread
        Thread(self._run_thread)


def pre_auton():
    """Called before autonomous - setup configuration screen"""
    # Don't use logger here since it will interfere with the screen
    pass




# =============================================================================
# PROGRAM STARTUP
# =============================================================================

# Initialize logger after all components are set up
logger.info("Logger initialized")

# Log program startup
logger.info("=== Robot Program Starting ===")
battery_voltage = str(round(brain.battery.voltage(), 1))
battery_current = str(round(brain.battery.current(), 1))
logger.info("Battery: " + battery_voltage + "V " + battery_current + "A")

# Create competition instance
comp = Competition(DriverControl.start, Autonomous.start)

# Start configuration screen in a separate thread
# This runs regardless of competition mode - in testing, it will show briefly
# In competition mode, it stays until Done is pressed or 5 seconds after last touch
config_screen = ConfigurationScreen(brain, logger, comp)
config_screen.run()

logger.info("Robot initialized and ready", ScreenTarget.BOTH)