import datetime
from numpy import asarray

# Размеры окна в пикселях
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

CELL_SIZE = 20

# Размеры сетки в ячейках
WIDTH = int(WINDOW_WIDTH / CELL_SIZE)
HEIGHT = int(WINDOW_HEIGHT / CELL_SIZE)

# Цвета
BG_COLOR = (0, 0, 0)
GRID_COLOR = (40, 40, 40)
APPLE_COLOR = (255, 0, 0)
APPLE_OUTER_COLOR = (155, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SNAKE_OUTER_COLOR = (0, 155, 0)

# UP = 'up'
# DOWN = 'down'
# LEFT = 'left'
# RIGHT = 'right'
UP = asarray([1., 0., 0., 0.])
DOWN = asarray([0., 1., 0., 0.])
LEFT = asarray([0., 0., 1., 0.])
RIGHT = asarray([0., 0., 0., 1.])

TURN_LEFT = asarray([1., 0., 0.])
TURN_RIGHT = asarray([0., 0., 1.])
DONT_TURN = asarray([0., 1., 0.])

# This is a list of possible moves. For convenience 3x same list.
# To find new direction after the turn left or right program will do +1 or -1 on this list.
# Base to do +1 or -1 is the 2nd occurrence of the direction in below list.
# That is why for ease I put direction 3 times:
# <look behind><main list><look ahead>
SNAKE_MOVE = [UP, RIGHT, DOWN, LEFT, UP, RIGHT, DOWN, LEFT, UP, RIGHT, DOWN, LEFT]

HEAD = 0

FPS = 1000

DEVICE = 'cuda'  # 'cuda' if torch.cuda.is_available() else 'cpu'

params = dict()
# Neural Network
params['epsilon_decay_linear'] = 1 / 100
params['learning_rate'] = 0.00013629
params['first_layer_size'] = 200  # neurons in the first layer
params['second_layer_size'] = 20  # neurons in the second layer
params['third_layer_size'] = 50  # neurons in the third layer
params['episodes'] = 500
params['memory_size'] = 2500
params['batch_size'] = 1000
# Settings
params['load_weights'] = True
params['weights_path'] = 'weights/weights.h5'
params['train'] = False
params["test"] = True
params['plot_score'] = True
params['display'] = False
# params['log_path'] = 'logs/scores_' + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + '.txt'
