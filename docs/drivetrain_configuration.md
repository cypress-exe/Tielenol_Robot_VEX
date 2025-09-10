# Drivetrain Configuration

## Motor Setup

The robot is configured with a 5-motor drivetrain system:

### Drive Motors (4 total)
- **Left Front Motor**: PORT1 (18:1 gear ratio, normal direction)
- **Left Back Motor**: PORT2 (18:1 gear ratio, normal direction)
- **Right Front Motor**: PORT3 (18:1 gear ratio, reversed direction)
- **Right Back Motor**: PORT4 (18:1 gear ratio, reversed direction)

### Strafing Motor
- **Strafe Motor**: PORT5 (18:1 gear ratio, normal direction)

### Sensors
- **Inertial Sensor**: PORT6 (for heading tracking)

## Motor Groups

For efficient control, the drive motors are organized into motor groups:

```python
# Left side motors work together
left_motor_group = MotorGroup(left_front_motor, left_back_motor)

# Right side motors work together  
right_motor_group = MotorGroup(right_front_motor, right_back_motor)
```

## Benefits of Motor Groups

1. **Synchronized Control**: All motors in a group receive identical commands
2. **Reduced Code**: Single command controls multiple motors
3. **Better Performance**: VEX optimizes motor group operations
4. **Simplified Logic**: The drivetrain abstraction treats groups like single motors

## Drivetrain Movement

The drivetrain supports holonomic movement with three degrees of freedom:

- **Forward/Backward**: Both left and right motor groups spin in same direction
- **Turn**: Left and right motor groups spin in opposite directions
- **Strafe**: Strafe motor moves robot sideways while maintaining heading

## Configuration

Motor configuration is defined in `src/configuration/robot_config.py`. To modify the setup:

1. Change port assignments in the `Motors` class
2. Adjust gear ratios as needed
3. Modify motor directions (reversed=True/False)
4. Update inertial sensor port if needed

The drivetrain abstraction automatically handles the motor groups without requiring changes to game mode code.
