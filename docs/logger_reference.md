# Enhanced Logger Quick Reference

## Overview
The enhanced logger provides comprehensive logging capabilities for VEX robotics projects with intelligent screen management and file organization.

## Key Features
- **Multiple log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Screen targeting**: Brain, Controller, Both, or Silent (file-only)
- **Automatic file management**: Up to 20 timestamped log files with automatic cleanup
- **Screen wrapping**: Intelligent screen management like the C++ example
- **Automatic cleanup**: Final log dump on program exit

## Quick Start

```python
from modules.logger import logger, LogLevel, ScreenTarget

# Basic logging (appears on both screens and in file)
logger.info("Robot initialized")
logger.warning("Low battery")
logger.error("Sensor failure")

# Target specific screens
logger.info("Brain only message", ScreenTarget.BRAIN)
logger.info("Controller only", ScreenTarget.CONTROLLER)
logger.silent("File only - no screen output")

# Set minimum log level
logger.set_log_level(LogLevel.WARNING)  # Only WARNING and above will be processed
```

## Log Levels (in order of severity)
1. **DEBUG** - Detailed debugging information
2. **INFO** - General information messages
3. **WARNING** - Warning messages for potential issues
4. **ERROR** - Error messages for failures
5. **CRITICAL** - Critical errors requiring immediate attention

## Screen Targets
- **ScreenTarget.BRAIN** - Only show on brain screen
- **ScreenTarget.CONTROLLER** - Only show on controller screen  
- **ScreenTarget.BOTH** - Show on both screens (default for most levels)
- **ScreenTarget.SILENT** - File logging only, no screen output

## Methods

### Basic Logging
```python
logger.debug(message, screen_target=ScreenTarget.BRAIN)
logger.info(message, screen_target=ScreenTarget.BOTH)
logger.warning(message, screen_target=ScreenTarget.BOTH)
logger.error(message, screen_target=ScreenTarget.BOTH)
logger.critical(message, screen_target=ScreenTarget.BOTH)
```

### Special Methods
```python
# Silent logging (file only)
logger.silent("Debug info", LogLevel.DEBUG)

# Legacy compatibility
logger.log("Message", LogLevel.INFO, ScreenTarget.BOTH)

# Manual log dump (usually automatic)
logger.dump()

# Level management
logger.set_log_level(LogLevel.WARNING)
current_level = logger.get_log_level()
```

## File Organization

### Configuration
Log saving can be enabled/disabled in `configuration/settings.py`:
```python
class LoggingSettings:
    SAVE_LOGS = True            # Set to False to disable file logging
    LOG_DIR = "/sd/logs/"       # Directory to save log files
    MAX_LOG_FILES = 20          # Maximum number of log files to keep
    DUMP_INTERVAL = 5           # Interval in seconds to auto-dump logs
```

### Log Files
- Directory: `/sd/logs/` (configurable)
- Files: `robot_log_YYYYMMDD_HHMMSS.txt`
- Retention: Maximum 20 files (oldest automatically deleted)
- **Note**: When `SAVE_LOGS = False`, no log files are created and no memory is used for buffering

## Screen Behavior

### Brain Screen
- Maximum 12 lines displayed
- Automatically wraps (clears and starts from top when full)
- Shows full formatted messages with timestamps

### Controller Screen
- Single line display (overwrites previous message)
- Messages truncated to 19 characters for display
- Most recent message always visible