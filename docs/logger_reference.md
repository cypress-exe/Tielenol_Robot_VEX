# Logger Quick Reference

## Overview
The logger provides screen-based logging capabilities for VEX robotics projects with intelligent screen management. This is screen-only logging system built for VEX V5 Brain and Controller displays.

## Key Features
- **Multiple log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Screen targeting**: Brain, Controller, or Both screens
- **Screen wrapping**: Intelligent screen management with automatic clearing
- **Formatted messages**: Timestamps and log level indicators

## Quick Start

```python
# Logger is already initialized in main.py as a global instance
# Basic logging (appears on both screens by default)
logger.info("Robot initialized")
logger.warning("Low battery")
logger.error("Sensor failure")

# Target specific screens
logger.info("Brain only message", ScreenTarget.BRAIN)
logger.info("Controller only", ScreenTarget.CONTROLLER)

# Set minimum log level
logger.set_log_level(LogLevel.WARNING)  # Only WARNING and above will be processed
```

## Log Levels (in order of severity)
1. **DEBUG** - Detailed debugging information (default: brain only)
2. **INFO** - General information messages (default: both screens)
3. **WARNING** - Warning messages for potential issues (default: both screens)
4. **ERROR** - Error messages for failures (default: both screens)
5. **CRITICAL** - Critical errors requiring immediate attention (default: both screens)

## Screen Targets
- **ScreenTarget.BRAIN** - Only show on brain screen
- **ScreenTarget.CONTROLLER** - Only show on controller screen  
- **ScreenTarget.BOTH** - Show on both screens (default for most levels)

## Methods

### Basic Logging
```python
logger.debug(message, screen_target=ScreenTarget.BRAIN)
logger.info(message, screen_target=ScreenTarget.BOTH)
logger.warning(message, screen_target=ScreenTarget.BOTH)
logger.error(message, screen_target=ScreenTarget.BOTH)
logger.critical(message, screen_target=ScreenTarget.BOTH)
```

### Utility Methods
```python
# Legacy compatibility
logger.log("Message", LogLevel.INFO, ScreenTarget.BOTH)

# Level management
logger.set_log_level(LogLevel.WARNING)
current_level = logger.get_log_level()
```

## Configuration

### LoggingSettings Class
```python
class LoggingSettings:
    """Logging configuration settings"""
    pass  # No settings needed for screen-only logging
```

## Screen Behavior

### Brain Screen
- Maximum 12 lines displayed (configurable via `max_brain_lines` parameter)
- Automatically wraps (clears and starts from top when full)
- Shows full formatted messages with timestamps and log levels
- Format: `[timestamp_ms] [LEVEL] message`

### Controller Screen
- Single line display (overwrites previous message)
- Messages truncated to 19 characters for display compatibility
- Most recent message always visible
- Simplified format for space constraints

## Usage Examples

### Typical Robot Startup
```python
logger.info("=== Robot Program Starting ===")
logger.info("Battery: " + str(brain.battery.voltage()) + "V")
logger.info("Robot initialized and ready", ScreenTarget.BOTH)
```

### Error Handling
```python
try:
    drivetrain.drive(forward, strafe, turn)
except Exception as e:
    logger.error("Drivetrain command failed: " + str(e))
```

### Debug Information (Brain Only)
```python
if abs(forward) > 50:
    debug_msg = "Driver input: F:" + str(int(forward))
    logger.debug(debug_msg, ScreenTarget.BRAIN)
```