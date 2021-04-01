from settings import *
import pygame
import random
from numpy import ndarray


class Cell:
    def __init__(self, x, y, display):
        self.x = x
        self.y = y
        self.display = display

    def draw_cell(self, outer_color, inner_color):
        # вспомогательная функция для рисования ячейки.
        #  Ячейка будет состоять из двух квадратов разных цветов:
        #  Больший квадрат закрашивается цветом outer_color,
        #  меньший - inner_color.
        #  Расстояние между внешним и внутренним квадратом
        #  принять за 4 пикселя.
        offset = 4
        block_outer = pygame.rect.Rect(self.x, self.y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.display, outer_color, block_outer, 0)
        block_inner = pygame.rect.Rect(self.x + offset / 2, self.y + offset / 2, CELL_SIZE - offset, CELL_SIZE - offset)
        pygame.draw.rect(self.display, inner_color, block_inner, 0)


class Apple:
    def __init__(self, cell: Cell):
        self.apple = cell

    def draw_apple(self):
        # нарисовать яблоко.
        self.apple.draw_cell(APPLE_OUTER_COLOR, APPLE_COLOR)

    def spawn(self, *args):
        # функция возвращает случайную ячейку,
        #  в которой будет располагаться яблоко.
        #  Для генерации случайной координаты воспользуйтесь
        #  функцией random.randint(a, b)
        new_apple_x = random.randint(1, WIDTH - 1)
        new_apple_y = random.randint(1, HEIGHT - 1)

        if args:
            while (new_apple_x, new_apple_y) in args:
                new_apple_x = random.randint(1, WIDTH - 1)
                new_apple_y = random.randint(1, HEIGHT - 1)

        self.apple.x, self.apple.y = WINDOW_WIDTH / WIDTH * new_apple_x, WINDOW_HEIGHT / HEIGHT * new_apple_y


class Snake:
    def __init__(self, *args: Cell):
        # создать змейку. Пусть она состоит из трех ячеек
        #  в строке 10 и столбцах 3, 4, 5.
        #  Какой тип данных удобен для представления змейки?
        self.body = [*args]
        # задать исходное направление движения змейки.
        self.direction: ndarray = RIGHT
        self.head = [*args][0]
        self.turn_direction: ndarray = DONT_TURN

    def draw_snake(self):
        # нарисовать змейку.
        for cell in self.body:
            cell.draw_cell(SNAKE_OUTER_COLOR, SNAKE_COLOR)

    def move(self):
        # реализовать перемещение змейки на одну ячейку
        #  в заданном направлении.
        #  * Какие параметры будет принимать функция?
        #  * Из каких действий будет состоять перемещение змейки?
        prev_pos = []
        for block in self.body:
            prev_pos.append((block.x, block.y))

        for _, block in enumerate(self.body):
            if _ == 0:
                if (self.direction == LEFT).all():
                    block.x -= WINDOW_WIDTH / WIDTH
                elif (self.direction == RIGHT).all():
                    block.x += WINDOW_WIDTH / WIDTH
                elif (self.direction == UP).all():
                    block.y -= WINDOW_HEIGHT / HEIGHT
                elif (self.direction == DOWN).all():
                    block.y += WINDOW_HEIGHT / HEIGHT
            else:
                block.x, block.y = prev_pos[_ - 1]

    def turn(self, matrix, prev_direction: ndarray, move_list: list):
        assert len(matrix) == 3, "Snake.turn() considers 3 possible actions."
        self.turn_direction = matrix
        to_left, stay, to_right = self.turn_direction
        shift = int(- 1 * to_left + 1 * to_right)
        if (prev_direction == UP).all():
            # 2nd occurrence of UP. need to explain why I take 2nd... just don't want bother with building a
            # good list I take SNAKE_MOVE = 3x snake_move, so when I pick 2nd occur and do -1 or +1 element
            # left or right I won't be out of bounds.
            up_pos = [i for i, n in enumerate(move_list) if (n == UP).all()][1]
            self.direction = move_list[up_pos + shift]
        elif (prev_direction == DOWN).all():
            down_pos = [i for i, n in enumerate(move_list) if (n == DOWN).all()][1]
            self.direction = move_list[down_pos + shift]
        elif (prev_direction == LEFT).all():
            left_pos = [i for i, n in enumerate(move_list) if (n == LEFT).all()][1]
            self.direction = move_list[left_pos + shift]
        elif (prev_direction == RIGHT).all():
            right_pos = [i for i, n in enumerate(move_list) if (n == RIGHT).all()][1]
            self.direction = move_list[right_pos + shift]

    def grow(self):
        # предложите максимально простой
        #  способ увеличения длины змейки.
        self.body.append(Cell(self.body[-1].x, self.body[-1].y, self.head.display))


def get_snake_new_head(snake: Snake):
    # реализовать функцию определения нового
    #  положения головы змейки.
    #  * Какие параметры будет принимать функция?
    #  * Что функция будет возвращать?
    return snake.body[0].x, snake.body[0].y


def snake_hit_edge(snake: Snake):
    # функция возвращает True,
    #  если змейка пересекла одну из границ окна.
    x, y = get_snake_new_head(snake)
    if any((x < 0, x >= WINDOW_WIDTH, y < 0, y >= WINDOW_HEIGHT)):
        return True


def snake_hit_apple(snake: Snake, apple: Apple):
    # функция возвращает True, если голова
    #  змейки находится в той же ячейке, что и яблоко.
    x, y = get_snake_new_head(snake)
    if x == apple.apple.x and y == apple.apple.y:
        return True


def get_direction(key_pressed, prev_direction):
    # функция возвращает направление движения
    #  в зависимости от нажатой клавиши:
    #  * pygame.K_LEFT
    #  * pygame.K_RIGHT
    #  * pygame.K_UP
    #  * pygame.K_DOWN
    #  Если нажата клавиша противоположного направления движения,
    #  то не менять направление.
    if key_pressed == pygame.K_UP and prev_direction != DOWN:
        return UP
    if key_pressed == pygame.K_UP and prev_direction == DOWN:
        return DOWN

    elif key_pressed == pygame.K_DOWN and prev_direction != UP:
        return DOWN
    elif key_pressed == pygame.K_DOWN and prev_direction == UP:
        return UP

    elif key_pressed == pygame.K_LEFT and prev_direction != RIGHT:
        return LEFT
    elif key_pressed == pygame.K_LEFT and prev_direction == RIGHT:
        return RIGHT

    elif key_pressed == pygame.K_RIGHT and prev_direction != LEFT:
        return RIGHT
    elif key_pressed == pygame.K_RIGHT and prev_direction == LEFT:
        return LEFT


def snake_hit_self(snake: Snake):
    # функция возвращает True, если голова змеи
    #  пересеклась хотя бы с одним блоком хвоста.
    head_pos = get_snake_new_head(snake)[0], get_snake_new_head(snake)[1]
    body_pos = [(block.x, block.y) for block in snake.body[1:]]

    if head_pos in body_pos:
        return True
