import sys
sys.path.append('src')
from rover_wheel_angle_calculator import RoverWheelAngleCalculator
import pygame

RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

FPS = 30

pygame.init()

pygame.display.set_caption('Rover Wheel Calculator Test')
window_surface = pygame.display.set_mode((800, 600))

SCREEN_DIMENSIONS = (800, 600)
SCREEN_CENTER = (int(SCREEN_DIMENSIONS[0]/2), int(SCREEN_DIMENSIONS[1]/2))
background = pygame.Surface(SCREEN_DIMENSIONS)
background.fill(WHITE)

# see equations.png for 'diagram' references in code comments
ROVER_Y = 10  # from center y length of rover to front wheels; should be the same distance as center to back
ROVER_X = 7  # full x width of rover
wheel_angle_calculator = RoverWheelAngleCalculator(

    # 'a' in diagram. If your wheels pivot from the center, your distance between front wheels is the same as
    # ROVER_X, and therefore your wheel gap distance term is 0.
    distance_between_front_wheels=ROVER_X,

    # 'c' in diagram
    distance_between_front_pivots=ROVER_X,

    # 'b' in diagram. For rover, this is half of length of rover
    distance_between_axels=ROVER_Y,

    # [min val, max val]
    joystick_range=[-100, 100],

    # 'linear' for now; 'log' will be enabled in future
    input_scale='linear'

)
ROVER_SIZE_TO_PIXEL_CONVERSION_SCALAR = 10
WHEEL_PIXEL_X_TERM = (ROVER_SIZE_TO_PIXEL_CONVERSION_SCALAR * (ROVER_X/2))
WHEEL_PIXEL_Y_TERM = (ROVER_SIZE_TO_PIXEL_CONVERSION_SCALAR * ROVER_Y)

# completely arbitrary valsfor this UI example
WHEEL_PIXEL_WIDTH = 10
WHEEL_PIXEL_HEIGHT = 20
# pygame rect position definition: Rect(left, top, width, height)
# going DOWN the screen is positive, don't get confused with screen y axis!
wheel_positions = [
    # left_front
    (
        SCREEN_CENTER[0] - WHEEL_PIXEL_X_TERM,  # rect leftmost position
        SCREEN_CENTER[1] - WHEEL_PIXEL_Y_TERM,  # rect topmost position
        WHEEL_PIXEL_WIDTH,
        WHEEL_PIXEL_HEIGHT
    ),
    # right_front
    (
        SCREEN_CENTER[0] + WHEEL_PIXEL_X_TERM,  # rect leftmost position
        SCREEN_CENTER[1] - WHEEL_PIXEL_Y_TERM,  # rect topmost position
        WHEEL_PIXEL_WIDTH,
        WHEEL_PIXEL_HEIGHT
    ),
    # left_back
    (
        SCREEN_CENTER[0] - WHEEL_PIXEL_X_TERM,  # rect leftmost position
        SCREEN_CENTER[1] + WHEEL_PIXEL_Y_TERM,  # rect topmost position
        WHEEL_PIXEL_WIDTH,
        WHEEL_PIXEL_HEIGHT
    ),
    # right_back
    (
        SCREEN_CENTER[0] + WHEEL_PIXEL_X_TERM,  # rect leftmost position
        SCREEN_CENTER[1] + WHEEL_PIXEL_Y_TERM,  # rect topmost position
        WHEEL_PIXEL_WIDTH,
        WHEEL_PIXEL_HEIGHT
    ),
]


def rectRotated(surface, color, pos, fill, border_radius, angle):
    """
    https://stackoverflow.com/questions/36510795/rotating-a-rectangle-not-image-in-pygame
    - angle in degree
    """
    max_area = max(pos[2], pos[3])
    s = pygame.Surface((max_area, max_area))
    s = s.convert_alpha()
    s.fill((0, 0, 0, 0))
    pygame.draw.rect(
        s,
        color,
        (0, 0, pos[2], pos[3]),
        # fill,
        border_radius=border_radius
    )
    s = pygame.transform.rotate(s, angle)
    surface.blit(s, (pos[0], pos[1]))
    return

def slider_pixel_x_to_percent(pixel_x_location):
    # handle div by 0
    if pixel_x_location == SCREEN_CENTER[0]:
        return 0.0
    # if pixel_x_location is on left half of screen, slider pct will be negative;
    # if pixel_x_location is on right half of screen, slider pct will be positive;
    # slider percent is scaled by half screen size so left size of screen is a slider
    # value of -100% and right side of screen is slider value of 100%
    slider_pct = ((pixel_x_location - SCREEN_CENTER[0]) / SCREEN_CENTER[0]) * 100
    return slider_pct


# slider widget thingy
slider_rect = pygame.rect.Rect(SCREEN_CENTER[0], SCREEN_CENTER[1], 20, 20)
slider_rect_dragging = False

clock = pygame.time.Clock()
is_running = True
offset_x = 0.0
offset_y = 0.0

while is_running:
    # handle user input
    for event in pygame.event.get():
        # exit game if user input said so
        if event.type == pygame.QUIT:
            is_running = False
        # handle user interaction with slider rect... only allow
        # user to move slider in x direction
        # handle user clicking onto slider rect
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if slider_rect.collidepoint(event.pos):
                    slider_rect_dragging = True
                    mouse_x, mouse_y = event.pos
                    offset_x = slider_rect.x - mouse_x
                    # offset_y = slider_rect.y - mouse_y
        # handle user letting go of click
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                slider_rect_dragging = False
        # handle user dragging rect
        elif event.type == pygame.MOUSEMOTION:
            if slider_rect_dragging:
                mouse_x, mouse_y = event.pos
                slider_rect.x = mouse_x + offset_x
                # slider_rect.y = mouse_y + offset_y
    # draw background
    window_surface.blit(background, (0, 0))
    # draw rover frame

    # draw joystick slider widget
    pygame.draw.rect(window_surface, RED, slider_rect)
    # calculate wheel rotations

    # draw wheels--make sure wheel_positions list is in same wheel order that
    # wheel_angles list is in!
    slider_pct = slider_pixel_x_to_percent(slider_rect.x)
    wheel_angles = wheel_angle_calculator.get_wheel_angles(slider_pct)
    for wheel_ix, wheel_angle in enumerate(wheel_angles):
        # flip the rotation of the wheel angle because pygame rotates counter-clockwise
        # and the RoverWheelAngleCalculator expects clockwise (RoverWheelAngleCalculator
        # sends negative angle meaning for wheel to rotate left from vertical, pygame
        # does opposite)
        wheel_angle *= -1
        # draw the rect at the specified rotation
        rectRotated(
            window_surface,
            BLACK,  # ignored
            wheel_positions[wheel_ix],
            WHITE,
            2,  # doesn't matter since fill is being ignored
            wheel_angle
        )
        # print(f"{wheel_ix}, {slider_pct}, {wheel_angle}")

    # update screen
    # pygame.display.update()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
