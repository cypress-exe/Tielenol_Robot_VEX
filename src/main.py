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

# =============================================================================
# SETTINGS CONFIGURATION
# =============================================================================

class DrivetrainSettings:
    """Drivetrain configuration settings"""
    FORWARD_BACKWARD_SPEED_MODIFIER = 1.0   # Modifier for forward/backward speed. Higher values increase speed.
    STRAFE_SPEED_MODIFIER = 1.0             # Modifier for strafing speed. Higher values increase speed.
    TURN_SPEED_MODIFIER = 0.25              # Modifier for turning speed. Higher values increase speed.

class ControllerSettings:
    """Controller configuration settings"""
    DEADZONE_THRESHOLD = 5  # Joystick deadzone threshold. Values within this range are ignored to prevent drift.
    
    FORWARD_BACKWARD_AXIS = 3
    STRAFE_AXIS = 4
    TURN_AXIS = 1

    INTAKE_BUTTON = 'R1'
    OUTPUT_LOW_BUTTON = 'R2'
    OUTPUT_MEDIUM_BUTTON = 'L2'
    OUTPUT_HIGH_BUTTON = 'L1'

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
        if self.brain_line > self.max_brain_lines:
            self.brain_line = 1
            self.brain.screen.clear_screen()
        
        # Split message into sections of 48 characters
        segments = []
        while len(message) > 48:
            segments.append(message[:48])
            message = message[48:]
        if message:
            segments.append(message)

        self.brain.screen.set_cursor(self.brain_line, 1)
        for segment in segments:
            self.brain.screen.print(segment)
            self.brain.screen.new_line()
            self.brain_line += 1

    def _log_to_controller(self, message: str):
        """Log message to controller screen (single line, overwrites)"""
        self.controller.screen.clear_line(1)
        self.controller.screen.set_cursor(1, 1)
        # Truncate message if too long for controller screen
        truncated_message = message[:19] if len(message) > 19 else message
        self.controller.screen.print(truncated_message)

    def _format_message(self, level, message):
        """Format message with timestamp and log level"""
        timestamp = self.brain.timer.time()  # ms since program start
        level_names = {1: "DEBUG", 2: "INFO", 3: "WARNING", 4: "ERROR", 5: "CRITICAL"}
        if level in level_names:
            level_name = level_names[level]
        else:
            level_name = 'UNKNOWN'
        return "[" + str(int(timestamp)) + "ms] [" + level_name + "] " + message

    def _log_internal(self, level, message, screen_target=ScreenTarget.BOTH):
        """Internal logging function"""
        if not self._should_log(level):
            return

        formatted_message = self._format_message(level, message)
        
        # Screen output
        if screen_target == ScreenTarget.BRAIN:
            self._log_to_brain(formatted_message)
        elif screen_target == ScreenTarget.CONTROLLER:
            self._log_to_controller(formatted_message)
        elif screen_target == ScreenTarget.BOTH:
            self._log_to_brain(formatted_message)
            self._log_to_controller(formatted_message)

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



    # Legacy compatibility method
    def log(self, message, level=LogLevel.INFO, screen_target=ScreenTarget.BOTH):
        """General log method for backwards compatibility"""
        self._log_internal(level, message, screen_target)



# =============================================================================
# CUSTOM CONTROLLER
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

# =============================================================================
# DRIVETRAIN ABSTRACTION
# =============================================================================

class Drivetrain:
    def __init__(
        self,
        left_motor: MotorGroup | Motor,
        right_motor: MotorGroup | Motor,
        strafe_motor: MotorGroup | Motor,
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

# =============================================================================
# ROBOT CONFIGURATION
# =============================================================================

# Global instances of motors and sensors
class Motors:
    # Individual drive motors
    left_front_motor = Motor(Ports.PORT7, GearSetting.RATIO_6_1, False)
    left_back_motor = Motor(Ports.PORT10, GearSetting.RATIO_6_1, False)
    right_front_motor = Motor(Ports.PORT9, GearSetting.RATIO_6_1, True)
    right_back_motor = Motor(Ports.PORT8, GearSetting.RATIO_6_1, True)
    
    # Strafing motor
    strafe_motor = Motor(Ports.PORT11, GearSetting.RATIO_18_1, False)
    
    # Motor groups for efficient control
    left_motor_group = MotorGroup(left_front_motor, left_back_motor)
    right_motor_group = MotorGroup(right_front_motor, right_back_motor)

    # Intake
    bottom_intake_motor = Motor(Ports.PORT6, GearSetting.RATIO_18_1, False)
    top_intake_motor = Motor(Ports.PORT20, GearSetting.RATIO_18_1, True)
    unloading_motor = Motor(Ports.PORT19, GearSetting.RATIO_18_1, True)

class Sensors:
    inertia_sensor = Inertial(Ports.PORT6)
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


# Initialize sensors
Sensors.initialize_sensors()

# Global instance of Controller & Brain
controller = CustomController()
brain = Brain()

# Create logger instance (requires brain and controller to be initialized)
logger = Logger(brain, controller)

# Drivetrain instance using motor groups
drivetrain = Drivetrain(Motors.left_motor_group, Motors.right_motor_group, Motors.strafe_motor, Sensors.inertia_sensor)

# =============================================================================
# BLOCK MANIPULATION SYSTEMS
# =============================================================================

class BlockManipulationSystemState:
    IDLE = 0
    INTAKING = 1
    OUTPUTTING_LOW = 2
    OUTPUTTING_MEDIUM = 3
    OUTPUTTING_HIGH = 4

class BlockManipulationSystem:
    def __init__(self):
        self.state = BlockManipulationSystemState.IDLE
        self.intaking = self.Intaking()
        self.outputting = self.Outputting()

    def set_state(self, new_state):
        self.state = new_state

    def update(self):
        """Main tick function to update the system based on current state"""
        if self.state == BlockManipulationSystemState.INTAKING:
            self.intaking.handle_intaking()
        elif self.state == BlockManipulationSystemState.OUTPUTTING_LOW:
            self.outputting.handle_output_low()
        elif self.state == BlockManipulationSystemState.OUTPUTTING_MEDIUM:
            self.outputting.handle_output_medium()
        elif self.state == BlockManipulationSystemState.OUTPUTTING_HIGH:
            self.outputting.handle_output_high()
        else:
            self.handle_idle()

    class Intaking:
        reject_current_block = False
        last_trigger_time = 0
        times_run = 0 # REMOVE LATER
        def handle_intaking(self):
            """Intaking logic"""
            self._check_current_block()
            Motors.bottom_intake_motor.spin(FORWARD, 100, PERCENT)
            Motors.top_intake_motor.spin(FORWARD if not self.reject_current_block else REVERSE, 100, PERCENT)
            Motors.unloading_motor.stop(BRAKE)

        def _check_current_block(self):
            """Check if the current block should be rejected based on vision sensor"""     
            def classify_color(hue):
                if 0 <= hue <= 10:
                    return 'RED'
                elif 120 <= hue <= 255:
                    return 'BLUE'
                else:
                    return 'UNKNOWN'
                
            # Turn on intake color sensor lights
            Sensors.intake_optical_sensor_left.set_light(LedStateType.ON)
            Sensors.intake_optical_sensor_right.set_light(LedStateType.ON)

            # Get current object from vision sensor
            left_hue = classify_color(Sensors.intake_optical_sensor_left.hue())
            right_hue = classify_color(Sensors.intake_optical_sensor_right.hue())

            # logger.info("Color: Left Hue: " + str(Sensors.intake_optical_sensor_left.hue()), ScreenTarget.BRAIN)

            if Sensors.intake_optical_sensor_right.is_near_object() or Sensors.intake_optical_sensor_left.is_near_object():
                # Red object detection
                if left_hue == 'RED' or right_hue == 'RED':
                    self.reject_current_block = False
                    self.last_trigger_time = brain.timer.time()
                    logger.info("Red block detected - accepting", ScreenTarget.BOTH)
                    return

                # Blue object detection
                if left_hue == 'BLUE' or right_hue == 'BLUE':
                    self.reject_current_block = True # TODO: HARD CODED FOR NOW
                    self.last_trigger_time = brain.timer.time()
                    logger.info("Blue block detected - rejecting", ScreenTarget.BOTH)
                    return
                
            TIME_DELAY_IN_MILLISECONDS = 1000
            if self.reject_current_block and ((brain.timer.time() - self.last_trigger_time) > TIME_DELAY_IN_MILLISECONDS):
                self.reject_current_block = False
                logger.info("No block detected - accepting by default", ScreenTarget.BOTH)

    class Outputting:
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
            Motors.bottom_intake_motor.spin(FORWARD, 100, PERCENT)
            Motors.top_intake_motor.spin(FORWARD, 100, PERCENT)
            Motors.unloading_motor.spin(REVERSE, 100, PERCENT)
    
    def handle_idle(self):
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

def autonomous_entrypoint():
    """Executed once upon entering autonomous mode"""
    logger.info("=== AUTONOMOUS MODE STARTED ===", ScreenTarget.BOTH)
    
    try:
        # Example autonomous routine with logging
        logger.info("Starting autonomous routine")
        
        # Add your autonomous code here
        # For example:
        # logger.info("Moving forward...")
        # drivetrain.drive_distance(1000)  # hypothetical method
        # logger.info("Turn completed")
        
        logger.info("Autonomous routine completed successfully")

    except Exception as e:
        logger.error("Autonomous routine failed: " + str(e))
        logger.error("Emergency stop activated", ScreenTarget.BOTH)
    logger.info("=== AUTONOMOUS MODE ENDED ===", ScreenTarget.BOTH)

# Track last significant input for logging
last_input_log_time = 0

def driver_control_entrypoint():
    """Executed once upon entering driver control mode"""
    logger.info("=== DRIVER CONTROL MODE STARTED ===", ScreenTarget.BOTH)
    
    try:
        drivetrain.set_stopping_mode(BRAKE)

        while True:
            update_drivetrain()
            update_block_manipulation_systems_state()

            # if controller.buttonUp.pressing():  # Example
            #     # brightness = Sensors.intake_optical_sensor.brightness()
            #     # logger.info("Brightness: " + str(brightness))
            #     # near = Sensors.intake_optical_sensor.is_near_object()
            #     # logger.info("Vision sensor <near>: " + str(near))
            #     # color = Sensors.intake_optical_sensor.color()
            #     hue = Sensors.intake_optical_sensor_right.hue()
            #     logger.info("Hue: " + str(hue))
            #     # Red: 0-10
            #     # Blue: 200-255

            wait(20, MSEC) # Run the loop every 20 milliseconds (50 times per second)
    except Exception as e:
        logger.critical("Driver control crashed: " + str(e))
        logger.critical("Robot stopped for safety", ScreenTarget.BOTH)
        logger.error("Restarting driver control mode...", ScreenTarget.BOTH)
        driver_control_entrypoint()  # Restart driver control mode

def update_drivetrain():
    """To be called repeatedly in driver control mode to update the drivetrain"""
    global last_input_log_time
    
    # Get joystick values with deadzone applied
    forward = controller.get_axis_with_deadzone(ControllerSettings.FORWARD_BACKWARD_AXIS)
    strafe = controller.get_axis_with_deadzone(ControllerSettings.STRAFE_AXIS)
    turn = controller.get_axis_with_deadzone(ControllerSettings.TURN_AXIS)

    # Log significant inputs occasionally (not every loop to avoid spam)
    current_time = brain.timer.time()
    if (abs(forward) > 50 or abs(strafe) > 50 or abs(turn) > 50) and \
       (current_time - last_input_log_time > 2000):  # Log every 2 seconds max
        debug_msg = "Driver input: F:" + str(int(forward)) + " S:" + str(int(strafe)) + " T:" + str(int(turn))
        logger.debug(debug_msg, ScreenTarget.BRAIN)
        last_input_log_time = current_time

    # Apply speed modifiers
    forward *= DrivetrainSettings.FORWARD_BACKWARD_SPEED_MODIFIER
    strafe *= DrivetrainSettings.STRAFE_SPEED_MODIFIER
    turn *= DrivetrainSettings.TURN_SPEED_MODIFIER

    # Command the drivetrain to move
    try:
        drivetrain.drive(forward, strafe, turn)
    except Exception as e:
        logger.error("Drivetrain command failed: " + str(e))

def update_block_manipulation_systems_state():
    """To be called repeatedly in driver control mode to update the block manipulation systems"""
    if controller.get_button(ControllerSettings.INTAKE_BUTTON).pressing(): # Intake
        block_manipulation_system.set_state(BlockManipulationSystemState.INTAKING)
    elif controller.get_button(ControllerSettings.OUTPUT_LOW_BUTTON).pressing(): # Output low
        block_manipulation_system.set_state(BlockManipulationSystemState.OUTPUTTING_LOW)
    elif controller.get_button(ControllerSettings.OUTPUT_MEDIUM_BUTTON).pressing(): # Output medium
        block_manipulation_system.set_state(BlockManipulationSystemState.OUTPUTTING_MEDIUM)
    elif controller.get_button(ControllerSettings.OUTPUT_HIGH_BUTTON).pressing(): # Output high
        block_manipulation_system.set_state(BlockManipulationSystemState.OUTPUTTING_HIGH)
    else:
        block_manipulation_system.set_state(BlockManipulationSystemState.IDLE)

    block_manipulation_system.update()


# =============================================================================
# MAIN PROGRAM
# =============================================================================

# Initialize logger after all components are set up
logger.info("Logger initialized")

# Log program startup
logger.info("=== Robot Program Starting ===")
battery_voltage = str(round(brain.battery.voltage(), 1))
battery_current = str(round(brain.battery.current(), 1))
logger.info("Battery: " + battery_voltage + "V " + battery_current + "A")

# Create competition instance
comp = Competition(driver_control_entrypoint, autonomous_entrypoint)

# Actions to do when the program starts
logger.info("Robot initialized and ready", ScreenTarget.BOTH)