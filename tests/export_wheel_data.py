import sys
sys.path.append('src')
from rover_wheel_angle_calculator import RoverWheelAngleCalculator


ROVER_Y = 10  # from center y length of rover to front wheels; should be the same distance as center to back
ROVER_X = 7  # full x width of rover
wheel_angle_calculator = RoverWheelAngleCalculator(
    distance_between_front_wheels=9,  # 'a' in diagram. For rover, this is half of length of rover
    distance_between_front_pivots=ROVER_X,  # 'c' in diagram
    distance_between_axels=ROVER_Y,  # 'b' in diagram
    joystick_range=[-100, 100],  # [min val, max val]
    input_scale='linear'  # 'log' or 'linear'; 'log' for smoothing out angle of wheel turn
)
wheel_angle_calculator.export_wheel_angles_table()
