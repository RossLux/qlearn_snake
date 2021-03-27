import pygame
import sys
import json
from numpy import asarray
from settings import *
from game import Cell, Snake, Apple
from game import get_snake_new_head, snake_hit_edge, snake_hit_apple, get_direction, snake_hit_self
from scoreboard import ScoreBoard
from datetime import datetime
from player1 import Agent

import torch.optim as optim


def get_state_in_json(player_score, high_score, head_pos, snake_pos, apple_pos, prev_direction):
    food_above = int(head_pos[1] < apple_pos.y)
    food_below = int(head_pos[1] > apple_pos.y)
    food_left = int(head_pos[0] > apple_pos.x)
    food_right = int(head_pos[0] < apple_pos.x)

    danger_above = int(head_pos[1] == CELL_SIZE) or \
                   int(any([block.y - head_pos[1] == CELL_SIZE and block.x == head_pos[0] for _, block in enumerate(snake_pos) if _ > 1]))
    danger_below = int(head_pos[1] == WINDOW_HEIGHT - CELL_SIZE) or \
                   int(any([head_pos[1] - block.y == CELL_SIZE and block.x == head_pos[0] for _, block in enumerate(snake_pos) if _ > 1]))
    danger_left = int(head_pos[0] == CELL_SIZE) or \
                  int(any([head_pos[0] - block.x == CELL_SIZE and block.y == head_pos[1] for _, block in enumerate(snake_pos) if _ > 1]))
    danger_right = int(head_pos[0] == WINDOW_WIDTH - CELL_SIZE) or \
                   int(any([block.x - head_pos[0] == CELL_SIZE and block.y == head_pos[1] for _, block in enumerate(snake_pos) if _ > 1]))

    return \
        {"Player Score: ": player_score,
         "High Score: ": high_score,
         "Head Position: ": head_pos,
         "Snake Position: ": [(block.x, block.y) for block in snake_pos],
         "Apple Position: ": (apple_pos.x, apple_pos.y),
         "Previous Direction: ": prev_direction,
         "Moving Up": int(prev_direction == 'up'),
         "Moving Down": int(prev_direction == 'down'),
         "Moving Left": int(prev_direction == 'left'),
         "Moving Right": int(prev_direction == 'right'),
         "Food Above: ": food_above,
         "Food Below: ": food_below,
         "Food Left: ": food_left,
         "Food Right: ": food_right,
         "Danger Above: ": danger_above,
         "Danger Below: ": danger_below,
         "Danger Left: ": danger_left,
         "Danger Right: ": danger_right
         }


def get_state(action_state):
    """
    Pass the Action #X json data and this will return np array of
            - Snake is moving Up
            - Snake is moving Down
            - Snake is moving Left
            - Snake is moving Right
            - The food is on the upper side
            - The food is on the lower side
            - The food is on the left
            - The food is on the right
            - Danger of hitting a wall or self is right above
            - Danger of hitting a wall or self is right below
            - Danger of hitting a wall or self is right on the left
            - Danger of hitting a wall or self is right on the right
    Format is like [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0].
    :param action_state: Action #X json data
    :return: numpy array
    """
    return asarray(list(action_state.values())[-12:])


def write_state_to_file(state, session_id):
    with open(f"./history/game-{session_id}.json", 'w') as fh:
        json.dump(state, fh, indent=4)


def main():
    # noinspection PyGlobalUndefined
    global FPS_CLOCK
    # noinspection PyGlobalUndefined
    global DISPLAY
    # noinspection PyGlobalUndefined
    global SCORE
    # noinspection PyGlobalUndefined
    global CURRENT_TIME
    now = datetime.now()
    CURRENT_TIME = now.strftime("%H-%M-%S")
    # noinspection PyGlobalUndefined
    global STATE
    # Initialize global dictionary that will contain information about the environment:
    # like, action taken, previous snake direction, current snake position, apple position etc.
    STATE = {}

    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    SCORE = ScoreBoard()

    # Create Player 1.
    agent = Agent(params).to_device()
    agent.optimizer = optim.Adam(agent.parameters(), weight_decay=0, lr=params['learning_rate'])

    # Game counter initialize.
    game_number = 1
    while game_number < params['episodes']:
        # Мы всегда будем начинать игру с начала. После проигрыша сразу
        # начинается следующая.
        run_game(game_number)
        # Increment game counter before start new game.
        game_number += 1


def run_game(game_number):
    # создать яблоко в позиции (20, 10)
    apple = Apple(Cell(WINDOW_WIDTH / WIDTH * 20, WINDOW_HEIGHT / HEIGHT * 10, DISPLAY))
    # создать змейку. Пусть она состоит из трех ячеек
    #  в строке 10 и столбцах 3, 4, 5.
    #  Какой тип данных удобен для представления змейки?
    snake = Snake(Cell(WINDOW_WIDTH / WIDTH * 5, WINDOW_HEIGHT / HEIGHT * 10, DISPLAY),
                  Cell(WINDOW_WIDTH / WIDTH * 4, WINDOW_HEIGHT / HEIGHT * 10, DISPLAY),
                  Cell(WINDOW_WIDTH / WIDTH * 3, WINDOW_HEIGHT / HEIGHT * 10, DISPLAY))

    # Reset player score.
    SCORE.player_score = 0

    # Initialize list containing tuples: (action, current state).
    action_state_list = []
    action_counter = 0

    while True:
        # Before snake does its first move, assign action = 'None'.
        action_counter += 1
        action = 'none'
        # Previous snake direction. We'll use as one of the current state parameters for evaluation.
        snake_prev_direction = snake.direction

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            # обработайте событие pygame.KEYDOWN
            #  и при необходимости измените направление движения змейки.
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # ESC key pressed
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                snake.direction = get_direction(event.key, snake.direction)  # Other key pressed
                # If any direction key was pressed - assign corresponding action.
                action = snake.direction

        # Appending the current action (could be 'None') and the current state of the snake to
        # the list - "Action-State List".
        action_state_list.append(({f"Action {action_counter}": action},
                                  get_state_in_json(player_score=SCORE.player_score,
                                                    high_score=SCORE.high_score,
                                                    head_pos=get_snake_new_head(snake),
                                                    snake_pos=snake.body,
                                                    apple_pos=apple.apple,
                                                    prev_direction=snake_prev_direction)

                                  ))
        # "Action-State List" to current game and write json on disk.
        STATE[f"Game #{game_number}"] = action_state_list

        # если змейка достигла границы окна, завершить игру.
        #  Для проверки воспользуйтесь функцией snake_hit_edge.
        if snake_hit_edge(snake):
            write_state_to_file(STATE, CURRENT_TIME)
            run_game(game_number + 1)

        # если змейка задела свой хвост, завершить игру.
        #  Для проверки восппользуйтесь функцией snake_hit_self.
        if snake_hit_self(snake):
            write_state_to_file(STATE, CURRENT_TIME)
            run_game(game_number + 1)

        # обработайте ситуацию столкновения змейки с яблоком.
        #  В этом случае нужно:
        #  * Увеличить размер змейки
        #  * Создать новое яблоко.
        if snake_hit_apple(snake, apple):
            snake.grow()
            apple.spawn([(block.x, block.y) for block in snake.body])  # check apple does not spawn on snake.
            SCORE.score()

        # сдвинуть змейку в заданном направлении
        snake.move()

        # передать яблоко в функцию отрисовки кадра
        # передать змейку в функцию отрисовки кадра
        draw_frame(snake, apple, SCORE)
        FPS_CLOCK.tick(FPS)


def draw_frame(snake, apple, score):
    DISPLAY.fill(BG_COLOR)
    draw_grid()
    show_score(score)
    snake.draw_snake()
    apple.draw_apple()
    pygame.display.update()


def draw_grid():
    # нарисовать сетку.
    #  Шаг CELL_SIZE
    #  Цвет GRID_COLOR
    #  https://www.pygame.org/docs/ref/draw.html#pygame.draw.line
    for x_pos in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(DISPLAY, GRID_COLOR, (x_pos, 0), (x_pos, WINDOW_HEIGHT))
    for y_pos in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(DISPLAY, GRID_COLOR, (0, y_pos), (WINDOW_WIDTH, y_pos))


def show_score(score):
    font = pygame.font.SysFont("Arial", 20, False, False)
    player_score = font.render("Score: " + str(score.player_score), True, (255, 255, 255))
    high_score = font.render("High Score: " + str(score.high_score), True, (255, 255, 255))
    DISPLAY.blit(player_score, (20, 20))
    DISPLAY.blit(high_score, (20, 40))


def terminate():
    write_state_to_file(STATE, CURRENT_TIME)
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
