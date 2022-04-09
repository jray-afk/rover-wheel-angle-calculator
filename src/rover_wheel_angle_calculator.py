import math
import pandas as pd
import statistics
import utils


class RoverWheelAngleCalculator:
    """
    See equations.png for help on how I derived these trigonometry functions.
    The equations accept wheel angles as input and output turn radius, but I inverted
    the equations so that they accept an input turn radius and then they output wheel
    angles... and gluing all that stuff to the rover problem are some other trig
    identities and nifty equations I threw in...

    Rover front and back wheels are mirrored, so 'rear' equations are ignored.
    """

    def __init__(self,
                 theta_max=44,
                 phi_max=30,
                 distance_between_front_wheels=9,  # 'a' in diagram. For rover, this is half of length of rover
                 distance_between_front_pivots=7,  # 'c' in diagram
                 distance_between_axels=10,  # 'b' in diagram
                 joystick_range=None,  # [max val left, max val right]
                 input_scale='linear'  # 'log' or 'linear'
                 ):
        # handle inputs
        self.theta_max = theta_max
        self.phi_max = phi_max
        self.distance_between_front_wheels = distance_between_front_wheels
        self.distance_between_front_pivots = distance_between_front_pivots
        self.distance_between_axels = distance_between_axels
        self.joystick_range = joystick_range
        if not self.joystick_range:
            self.joystick_range = [-100, 100]
        self.input_scale = input_scale
        if self.input_scale not in ['log', 'linear']:
            raise Exception("Error: input_scale must be 'log' or 'linear'.")
        # TODO: enable log scale
        if self.input_scale == 'log':
            raise Exception("Error: log scale not enabled yet. Try linear instead.")
        # define internal vars
        self.joystick_direction = 'center'
        self.wheel_gap_distance = ((self.distance_between_front_wheels - self.distance_between_front_pivots)/2)  # '(a-c)/2'
        self.joystick_midpoint = statistics.mean(self.joystick_range)
        # complete object initialization
        # these params are lazy and will only be filled if needed
        self.practical_center_point_range_linear = None
        self.practical_center_point_range_logscale = None
        return

    def get_wheel_turn_radius_inner_front(self, theta):
        return (self.distance_between_axels / math.sin(theta)) - self.wheel_gap_distance

    def get_wheel_turn_radius_outer_front(self, phi):
        return (self.distance_between_axels / math.sin(phi)) + self.wheel_gap_distance

    # def get_wheel_turn_radius_inner_rear(self, theta):
    #     return (self.distance_between_axels / math.tan(theta)) - self.wheel_gap_distance
    #
    # def get_wheel_turn_radius_outer_rear(self, phi):
    #     return (self.distance_between_axels / math.tan(phi)) + self.wheel_gap_distance

    def get_wheel_theta_inner_front(self, if_turn_radius):
        val = self.distance_between_axels / (if_turn_radius + self.wheel_gap_distance)
        val = utils.clamp(val, -1.0, 1.0)
        return math.asin(val)

    def get_wheel_phi_outer_front(self, of_turn_radius):
        # print(of_turn_radius, self.distance_between_axels, self.wheel_gap_distance)
        val = self.distance_between_axels / (of_turn_radius - self.wheel_gap_distance)
        val = utils.clamp(val, -1.0, 1.0)
        return math.asin(val)

    # def get_wheel_theta_inner_rear(ir_turn_radius):
    #     return
    #
    # def get_wheel_phi_outer_rear(or_turn_radius):
    #     return

    def get_max_turn_radii(self):
        # radius_inner_front = self.get_wheel_turn_radius_inner_front(self.theta_max)
        # radius_outer_front = self.get_wheel_turn_radius_outer_front(self.phi_max)
        # radius_inner_rear = self.get_wheel_turn_radius_inner_rear(self.theta_max)
        # radius_outer_rear = self.get_wheel_turn_radius_outer_rear(self.phi_max)
        # return radius_inner_front, radius_outer_front, radius_inner_rear, radius_outer_rear
        radius_inner = self.get_wheel_turn_radius_inner_front(self.theta_max)
        radius_outer = self.get_wheel_turn_radius_outer_front(self.phi_max)
        return radius_inner, radius_outer

    def calc_practical_center_point_range_linear(self):
        """

        :return:
        """
        max_turn_radii = self.get_max_turn_radii()
        min_practical_center_point = (self.distance_between_axels * math.sin(90 - self.theta_max)) + self.distance_between_front_pivots
        max_practical_center_point = math.sqrt(
            (max_turn_radii[0] ** 2) - (self.distance_between_axels ** 2)) + self.distance_between_front_pivots
        center_point_range = [min_practical_center_point, max_practical_center_point]
        return center_point_range

    def get_practical_center_point_range_linear(self):
        """
        If already calculated, grab value stored to object. If not, then calculate.
        :return:
        """
        if self.practical_center_point_range_linear:
            return self.practical_center_point_range_linear
        self.practical_center_point_range_linear = self.calc_practical_center_point_range_linear()
        return self.practical_center_point_range_linear

    def calc_practical_center_point_range_logscale(self):
        """
        The relationship between center point value (independent variable, i.e. x axis if plotted) and
        wheel angle (dependent variable, i.e. y axis if plotted) is a power function. This function applies
        a log transform to linearize the power scale. This means if that the user inputs a center point on
        a linear range, they can expect to get a smoother more linear output in wheel angle rather than
        exponential changes to wheel angle with center point inputs.
        :return:
        """
        center_point_range = self.get_practical_center_point_range_linear()
        center_point_range_logscale = [
            math.log(center_point_range[0]),
            math.log(center_point_range[1])
        ]
        return center_point_range_logscale

    def get_practical_center_point_range_logscale(self):
        """
        If already calculated, grab value stored to object. If not, then calculate.
        :return:
        """
        if self.practical_center_point_range_logscale:
            return self.practical_center_point_range_logscale
        self.practical_center_point_range_logscale = self.calc_practical_center_point_range_logscale()
        return self.practical_center_point_range_logscale

    def get_practical_center_point_range(self):
        if self.input_scale == 'log':
            return self.get_practical_center_point_range_logscale()
        elif self.input_scale == 'linear':
            return self.get_practical_center_point_range_linear()
        else:
            raise Exception("Error: input_scale must be either 'log' or 'linear'.")
        return

    def get_wheel_angles_from_center_point(self, center_point):
        # get the x distance
        if_x = center_point - self.distance_between_front_pivots
        of_x = center_point
        # pythagorean theorem!! eureka!!!!!!!!!! we have the bottom edge of the inner front wheel's
        # triangle and the height, now we just need to solve for the hypotenuse (the turn radius)!
        # Then with the turn radius we can calculate the wheel angle!!!!!!!!
        if_turn_radius = math.sqrt((if_x ** 2) + (self.distance_between_axels ** 2))
        if_angle = math.degrees(self.get_wheel_theta_inner_front(if_turn_radius))
        # print(if_turn_radius, if_angle)
        # print(center_point, if_angle)
        of_turn_radius = math.sqrt((of_x ** 2) + (self.distance_between_axels ** 2))
        of_angle = math.degrees(self.get_wheel_phi_outer_front(of_turn_radius))
        # print(of_turn_radius, of_angle)
        return if_angle, of_angle

    def export_wheel_angles_table(self, joystick_input_step_size=None):
        # fill default if none supplied
        if not joystick_input_step_size:
            if self.input_scale == 'log':
                joystick_input_step_size = 0.1
            elif self.input_scale == 'linear':
                joystick_input_step_size = 10
        # collect wheel angle data points for a practical input range of center points
        all_data_points = []
        center_point_range = self.get_practical_center_point_range()
        for joystick_val in range(self.joystick_range[0], self.joystick_range[1], joystick_input_step_size):
            joystick_direction = self.get_joystick_direction(joystick_val)
            center_point = self.get_scaled_center_point_input_from_joystick_input(joystick_val, joystick_direction)
            if_angle, of_angle = self.get_wheel_angles_from_center_point(center_point)
            if joystick_val == 0.0 or joystick_direction == 'center':
                if_angle = 0.0
                of_angle = 0.0
            data = {
                'input_value': joystick_val,
                'turn_direction': joystick_direction,
                'inner_wheel_angle': if_angle,
                'outer_wheel_angle': of_angle
            }
            all_data_points.append(data)
            print(
                f"CENTER_POINT: {center_point}, INNER FRONT WHEEL ANGLE: {if_angle}, OUTER FRONT WHEEL ANGLE: {of_angle}")
        # save the data
        df = pd.DataFrame(all_data_points)
        df.to_csv('wheel_angles.csv', index=False)
        # notify user
        print("Wheel angles export table saved to 'wheel_angles.csv'.")
        return

    def get_scaled_center_point_input_from_joystick_input(self, joystick_val, joystick_direction):
        """
        The diagram from which the equations were derived used LEFT as the reference, therefore this is why
        the output of this function has LEFT as positive and RIGHT as negative.
        :param joystick_val:
        :param joystick_direction:
        :return:
        """
        center_point_range = self.get_practical_center_point_range()
        old_range = self.joystick_range[1] - self.joystick_range[0]
        new_range = center_point_range[1] - center_point_range[0]
        scaled_val = (((joystick_val - self.joystick_range[0]) * new_range) / old_range) + center_point_range[0]
        # for right inputs, we don't want them to keep climbing, we want to reflect the line over the horizontal
        # midpoint value of the new_range so they mirror the left values
        if joystick_direction == 'right':
            scaled_val = scaled_val - new_range
        # print(joystick_val, old_range, new_range, scaled_val)
        return scaled_val

    def get_joystick_direction(self, joystick_val):
        js_dir = 'center'
        if joystick_val < self.joystick_midpoint:
            js_dir = 'left'
        elif joystick_val > self.joystick_midpoint:
            js_dir = 'right'
        self.joystick_direction = js_dir
        return js_dir

    def get_wheel_angles(self, joystick_val):
        """
        Input a joystick value and receive wheel angles for each of the 4 rover tires (inner_front,
        outer_front, inner_back, outer_back).

        In the case of a rover, back wheel angles mirror front wheel angles. This is not the same
        as a normal car in the equations.png diagram!

        :param joystick_val:
        :return:
        """
        # the value is now scaled to its appropriate log/linear range. If scaled to log range,
        # we need to convert the log(center_point) value to an actual center_point value, i.e.
        # do the inverse of log,
        if self.input_scale == 'log':
            joystick_val = 10 ** joystick_val
        joystick_val = utils.clamp(joystick_val, self.joystick_range[0], self.joystick_range[1])
        joystick_direction = self.get_joystick_direction(joystick_val)
        left_front = 0.0
        right_front = 0.0
        left_back = 0.0
        right_back = 0.0
        # if not turning, all tire angles are 0
        if joystick_val == 0.0 or joystick_direction == 'center':
            return left_front, right_front, left_back, right_back
        # print(joystick_val)

        # calculate each wheel's angle from the horizontal
        center_point = self.get_scaled_center_point_input_from_joystick_input(joystick_val, joystick_direction)
        # print(center_point)
        inner_angle, outer_angle = self.get_wheel_angles_from_center_point(center_point)
        # print(inner_angle, outer_angle)
        if joystick_direction == 'left':
            # calculate relative wheels to turn
            # if turning left, front wheel angles are negative, back wheel angles are positive
            inner_front = -1 * inner_angle
            outer_front = -1 * outer_angle
            inner_back = inner_angle
            outer_back = outer_angle
            # translate to actual wheel; left wheels are inner wheels when turning left,
            # right wheels are outer wheels when turning left
            left_front = utils.clamp(inner_front, -self.theta_max, self.theta_max)
            right_front = utils.clamp(outer_front, -self.phi_max, self.phi_max)
            left_back = utils.clamp(inner_back, -self.theta_max, self.theta_max)
            right_back = utils.clamp(outer_back, -self.phi_max, self.phi_max)
        elif joystick_direction == 'right':
            # calculate relative wheels to turn
            # if turning right, front tire angles are positive, back tire angles are negative
            inner_front = inner_angle
            outer_front = outer_angle
            inner_back = -1 * inner_angle
            outer_back = -1 * outer_angle
            # translate to actual wheel; left wheels are outer wheels when turning right,
            # right wheels are inner wheels when turning right
            left_front = utils.clamp(outer_front, -self.phi_max, self.phi_max)
            right_front = utils.clamp(inner_front, -self.theta_max, self.theta_max)
            left_back = utils.clamp(outer_back, -self.phi_max, self.phi_max)
            right_back = utils.clamp(inner_back, -self.theta_max, self.theta_max)
        return left_front, right_front, left_back, right_back







