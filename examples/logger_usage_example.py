"""
Logger Usage Example

This example demonstrates how to use the enhanced logger system,
including how to configure log saving.
"""

# To enable/disable log saving, modify configuration/settings.py:
# class LoggingSettings:
#     SAVE_LOGS = True   # Set to False to disable file logging

from modules.logger import logger, LogLevel, ScreenTarget

def main():
    # Basic logging examples
    logger.info("Robot program started")
    logger.warning("Battery voltage low")
    logger.error("Sensor disconnected")
    
    # Screen targeting examples
    logger.info("This appears on brain only", ScreenTarget.BRAIN)
    logger.info("Controller message", ScreenTarget.CONTROLLER)
    logger.silent("This only goes to file (if enabled)")
    
    # Log level filtering
    logger.set_log_level(LogLevel.WARNING)
    logger.debug("This won't appear - below WARNING level")
    logger.warning("This will appear - WARNING level")
    
    # Manual log dump (usually automatic)
    logger.dump()
    
    logger.info("Example complete")

if __name__ == "__main__":
    main()