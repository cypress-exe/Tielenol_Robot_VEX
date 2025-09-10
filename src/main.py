# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       Dirk                                                         #
# 	Created:      9/4/2025, 2:20:48 PM                                         #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *

# Project imports
from configuration.robot_config import brain
from game_modes.autonomous import autonomous_entrypoint
from game_modes.drivercontrol import driver_control_entrypoint
from modules.logger import logger, LogLevel, ScreenTarget

# Log program startup
logger.info("=== Robot Program Starting ===")
logger.info(f"Battery: {brain.battery.voltage():.1f}V {brain.battery.current():.1f}A")

# Create competition instance
comp = Competition(driver_control_entrypoint, autonomous_entrypoint)

# Actions to do when the program starts
logger.info("Robot initialized and ready", ScreenTarget.BOTH)