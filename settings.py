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

HEAD = 0

FPS = 100

DEVICE = 'cuda'  # 'cuda' if torch.cuda.is_available() else 'cpu'

params = dict()
# Neural Network
params['epsilon_decay_linear'] = 1 / 100
params['learning_rate'] = 0.00013629
params['first_layer_size'] = 200  # neurons in the first layer
params['second_layer_size'] = 20  # neurons in the second layer
params['third_layer_size'] = 50  # neurons in the third layer
params['episodes'] = 250
params['memory_size'] = 2500
params['batch_size'] = 1000
# Settings
params['load_weights'] = True
params['weights_path'] = 'weights/weights.h5'
params['train'] = True
params["test"] = False
params['plot_score'] = False
# params['log_path'] = 'logs/scores_' + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + '.txt'
