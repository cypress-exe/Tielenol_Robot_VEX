from vex import Controller

from configuration.settings import ControllerSettings

class CustomController(Controller):
    def get_axis(self, axis):
        "Returns the specified axis of the controller"
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
        "Returns the specified axis of the controller with deadzone applied"
        value = self.get_axis(axis).position()
        if abs(value) < ControllerSettings.DEADZONE_THRESHOLD:
            return 0
        return value