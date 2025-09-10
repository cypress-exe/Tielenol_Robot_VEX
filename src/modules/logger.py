import time
import os
import glob
import atexit
from datetime import datetime
from enum import Enum

from configuration.robot_config import brain, controller
from configuration.settings import LoggingSettings

# Log directory and settings
SAVE_LOGS = LoggingSettings.SAVE_LOGS
LOG_DIR = LoggingSettings.LOG_DIR
MAX_LOG_FILES = LoggingSettings.MAX_LOG_FILES

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
    def __init__(self, dump_interval=None, max_brain_lines=12):
        self.buffer = []
        self.last_dump = time.time()
        self.dump_interval = dump_interval or LoggingSettings.DUMP_INTERVAL
        self.current_log_level = LogLevel.INFO
        
        # Screen management
        self.brain_line = 1
        self.max_brain_lines = max_brain_lines
        
        # File management
        self.save_logs = SAVE_LOGS
        if self.save_logs:
            self.log_dir = LOG_DIR
            self.log_file_path = self._create_log_file()
            # Cleanup old logs
            self._cleanup_old_logs()
        else:
            self.log_file_path = ""
        
        # Register cleanup on exit
        atexit.register(self._final_dump)
        
        # Initial log
        self.info("Logger initialized")

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
            
            if len(log_files) > MAX_LOG_FILES:
                # Sort by modification time (oldest first)
                log_files.sort(key=os.path.getmtime)
                
                # Remove oldest files
                files_to_remove = log_files[:-MAX_LOG_FILES]
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
            brain.screen.clear_screen()
        
        brain.screen.set_cursor(self.brain_line, 1)
        brain.screen.print(message)
        brain.screen.new_line()
        self.brain_line += 1

    def _log_to_controller(self, message: str):
        """Log message to controller screen (single line, overwrites)"""
        controller.screen.clear_line(1)
        controller.screen.set_cursor(1, 1)
        # Truncate message if too long for controller screen
        truncated_message = message[:19] if len(message) > 19 else message
        controller.screen.print(truncated_message)

    def _format_message(self, level: LogLevel, message: str) -> str:
        """Format message with timestamp and log level"""
        timestamp = brain.timer.time()  # ms since program start
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

# Create global logger instance
logger = Logger()