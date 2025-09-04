# Library imports
from vex import *

# Project imports
from configuration.robot_config import drivetrain, controller, brain
from configuration.settings import ControllerSettings, DrivetrainSettings

def autonomous_entrypoint():
    '''Executed once upon entering autonomous mode'''
    brain.screen.clear_screen()
    brain.screen.print("Running autonomous code.")
    