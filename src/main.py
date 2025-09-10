# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py (Monolithic)                                         #
# 	Author:       Dirk                                                         #
# 	Created:      9/4/2025, 2:20:48 PM                                         #
# 	Description:  V5 project - All modules combined into single file          #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *
import time
import os
import glob
import atexit
from datetime import datetime
from enum import Enum

# =============================================================================
# SETTINGS CONFIGURATION
# =============================================================================

class DrivetrainSettings:
    """Drivetrain configuration settings"""
    FORWARD_BACKWARD_SPEED_MODIFIER = 1.0  # Modifier for forward/backward speed. Higher values increase speed.
    STRAFE_SPEED_MODIFIER = 1.0             # Modifier for strafing speed. Higher values increase speed.
    TURN_SPEED_MODIFIER = 1.0               # Modifier for turning speed. Higher values increase speed.

class ControllerSettings:
    """Controller configuration settings"""
    DEADZONE_THRESHOLD = 5  # Joystick deadzone threshold. Values within this range are ignored to prevent drift.
    
    FORWARD_BACKWARD_AXIS = 2
    STRAFE_AXIS = 1
    TURN_AXIS = 4

class LoggingSettings:
    """Logging configuration settings"""
    SAVE_LOGS = False           # Enable/disable saving logs to file
    LOG_DIR = "/sd/logs/"       # Directory to save log files
    MAX_LOG_FILES = 20          # Maximum number of log files to keep
    DUMP_INTERVAL = 5           # Interval in seconds to auto-dump logs to file

# =============================================================================
# LOGGING SYSTEM
# =============================================================================

class LogLevel(Enum):
    """Log levels in order of severity"""
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5

class ScreenTarget(Enum):
    """Screen output targets"""
    BRAIN = 1
    CONTROLLER = 2
    BOTH = 3
    SILENT = 4  # No screen output, only file logging

class Logger:
    def __init__(self, brain_instance, controller_instance, dump_interval=None, max_brain_lines=12):
        self.brain = brain_instance
        self.controller = controller_instance
        self.buffer = []
        self.last_dump = time.time()
        self.dump_interval = dump_interval or LoggingSettings.DUMP_INTERVAL
        self.current_log_level = LogLevel.INFO
        
        # Screen management
        self.brain_line = 1
        self.max_brain_lines = max_brain_lines
        
        # File management
        self.save_logs = LoggingSettings.SAVE_LOGS
        if self.save_logs:
            self.log_dir = LoggingSettings.LOG_DIR
            self.log_file_path = self._create_log_file()
            # Cleanup old logs
            self._cleanup_old_logs()
        else:
            self.log_file_path = ""
        
        # Register cleanup on exit
        atexit.register(self._final_dump)

    def _create_log_file(self) -> str:
        """Create a new log file with timestamp"""
        if not self.save_logs: return ""

        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"robot_log_{timestamp}.txt"
        log_path = os.path.join(self.log_dir, log_filename)
        
        # Create initial log entry
        with open(log_path, 'w') as f:
            f.write(f"=== Robot Log Started at {datetime.now().isoformat()} ===\n")
            f.write("=" * 50 + "\n\n")
        
        return log_path

    def _cleanup_old_logs(self):
        """Remove old log files, keeping only the most recent MAX_LOG_FILES"""
        if not self.save_logs: return
        try:
            log_pattern = os.path.join(self.log_dir, "robot_log_*.txt")
            log_files = glob.glob(log_pattern)
            
            if len(log_files) > LoggingSettings.MAX_LOG_FILES:
                # Sort by modification time (oldest first)
                log_files.sort(key=os.path.getmtime)
                
                # Remove oldest files
                files_to_remove = log_files[:-LoggingSettings.MAX_LOG_FILES]
                for file_path in files_to_remove:
                    try:
                        os.remove(file_path)
                        print(f"Removed old log file: {os.path.basename(file_path)}")
                    except Exception as e:
                        print(f"Failed to remove {file_path}: {e}")
        except Exception as e:
            print(f"Log cleanup failed: {e}")

    def set_log_level(self, level: LogLevel):
        """Set the minimum log level that will be processed"""
        self.current_log_level = level
        self.info(f"Log level set to {level.name}")

    def get_log_level(self) -> LogLevel:
        """Get the current log level"""
        return self.current_log_level

    def _should_log(self, level: LogLevel) -> bool:
        """Check if a message should be logged based on current log level"""
        return level.value >= self.current_log_level.value

    def _log_to_brain(self, message: str):
        """Log message to brain screen with wrapping"""
        if self.brain_line > self.max_brain_lines:
            self.brain_line = 1
            self.brain.screen.clear_screen()
        
        self.brain.screen.set_cursor(self.brain_line, 1)
        self.brain.screen.print(message)
        self.brain.screen.new_line()
        self.brain_line += 1

    def _log_to_controller(self, message: str):
        """Log message to controller screen (single line, overwrites)"""
        self.controller.screen.clear_line(1)
        self.controller.screen.set_cursor(1, 1)
        # Truncate message if too long for controller screen
        truncated_message = message[:19] if len(message) > 19 else message
        self.controller.screen.print(truncated_message)

    def _format_message(self, level: LogLevel, message: str) -> str:
        """Format message with timestamp and log level"""
        timestamp = self.brain.timer.time()  # ms since program start
        return f"[{timestamp:8.0f}ms] [{level.name:8s}] {message}"

    def _log_internal(self, level: LogLevel, message: str, screen_target: ScreenTarget = ScreenTarget.BOTH):
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
        # SILENT means no screen output

        # Only add to buffer if saving logs
        if self.save_logs:
            self.buffer.append(formatted_message)

            # Auto-dump if interval passed
            if time.time() - self.last_dump >= self.dump_interval:
                self.dump()

    # Public logging methods
    def debug(self, message: str, screen_target: ScreenTarget = ScreenTarget.BRAIN):
        """Log debug message"""
        self._log_internal(LogLevel.DEBUG, message, screen_target)

    def info(self, message: str, screen_target: ScreenTarget = ScreenTarget.BOTH):
        """Log info message"""
        self._log_internal(LogLevel.INFO, message, screen_target)

    def warning(self, message: str, screen_target: ScreenTarget = ScreenTarget.BOTH):
        """Log warning message"""
        self._log_internal(LogLevel.WARNING, message, screen_target)

    def error(self, message: str, screen_target: ScreenTarget = ScreenTarget.BOTH):
        """Log error message"""
        self._log_internal(LogLevel.ERROR, message, screen_target)

    def critical(self, message: str, screen_target: ScreenTarget = ScreenTarget.BOTH):
        """Log critical message"""
        self._log_internal(LogLevel.CRITICAL, message, screen_target)

    def silent(self, message: str, level: LogLevel = LogLevel.INFO):
        """Log message silently (file only, no screen output)"""
        self._log_internal(level, message, ScreenTarget.SILENT)

    # Legacy compatibility method
    def log(self, message: str, level: LogLevel = LogLevel.INFO, screen_target: ScreenTarget = ScreenTarget.BOTH):
        """General log method for backwards compatibility"""
        self._log_internal(level, message, screen_target)

    def dump(self):
        """Dump buffer to log file"""
        if not self.save_logs or not self.buffer:
            return
            
        try:
            with open(self.log_file_path, "a") as f:
                f.write("\n".join(self.buffer) + "\n")
            self.buffer.clear()
            self.last_dump = time.time()
        except Exception as e:
            print(f"Log dump failed: {e}")

    def _final_dump(self):
        """Final log dump called on program exit"""
        if self.save_logs:
            self.info("Program ending - performing final log dump", ScreenTarget.SILENT)
            self.dump()
            
            # Add final entry to log file
            try:
                with open(self.log_file_path, "a") as f:
                    f.write(f"\n=== Program ended at {datetime.now().isoformat()} ===\n")
            except Exception as e:
                print(f"Final log entry failed: {e}")

# =============================================================================
# CUSTOM CONTROLLER
# =============================================================================

class CustomController(Controller):
    def get_axis(self, axis):
        """Returns the specified axis of the controller"""
        match axis:
            case 1:
                return self.axis1
            case 2:
                return self.axis2
            case 3:
                return self.axis3
            case 4:
                return self.axis4
            case _:
                raise ValueError("Invalid axis")
            
    def get_axis_with_deadzone(self, axis):
        """Returns the specified axis of the controller with deadzone applied"""
        value = self.get_axis(axis).position()
        if abs(value) < ControllerSettings.DEADZONE_THRESHOLD:
            return 0
        return value

# =============================================================================
# DRIVETRAIN ABSTRACTION
# =============================================================================

class Drivetrain:
    def __init__(
        self,
        left_motor,
        right_motor,
        strafe_motor,
        inertia_sensor,
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

    def drive(self, forward: float, strafe: float, turn: float):
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
    
    def set_velocity(self, velocity: float, units=PERCENT):
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

# Create logger instance (requires brain and controller to be initialized)
logger = Logger(brain, controller)

# Drivetrain instance using motor groups
drivetrain = Drivetrain(Motors.left_motor_group, Motors.right_motor_group, Motors.strafe_motor, Sensors.inertia_sensor)

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
        logger.error(f"Autonomous routine failed: {e}")
        logger.error("Emergency stop activated", ScreenTarget.BOTH)
    
    logger.info("=== AUTONOMOUS MODE ENDED ===", ScreenTarget.BOTH)

# Track last significant input for logging
last_input_log_time = 0

def driver_control_entrypoint():
    """Executed once upon entering driver control mode"""
    logger.info("=== DRIVER CONTROL MODE STARTED ===", ScreenTarget.BOTH)
    
    try:
        while True:
            drivetrain_update()
            wait(20, MSEC) # Run the loop every 20 milliseconds (50 times per second)
    except Exception as e:
        logger.critical(f"Driver control crashed: {e}")
        logger.critical("Robot stopped for safety", ScreenTarget.BOTH)

def drivetrain_update():
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

# =============================================================================
# MAIN PROGRAM
# =============================================================================

# Initialize logger after all components are set up
logger.info("Logger initialized")

# Log program startup
logger.info("=== Robot Program Starting ===")
logger.info(f"Battery: {brain.battery.voltage():.1f}V {brain.battery.current():.1f}A")

# Create competition instance
comp = Competition(driver_control_entrypoint, autonomous_entrypoint)

# Actions to do when the program starts
logger.info("Robot initialized and ready", ScreenTarget.BOTH)