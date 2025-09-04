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

# Create competition instance
comp = Competition(driver_control_entrypoint, autonomous_entrypoint)

# Actions to do when the program starts
brain.screen.clear_screen()