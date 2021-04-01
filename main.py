import random
import numpy as np
import torch
import pygame
import sys
import json
from settings import *
from game import Cell, Snake, Apple
from game import get_snake_new_head, snake_hit_edge, snake_hit_apple, get_direction, snake_hit_self
from scoreboard import ScoreBoard
from datetime import datetime
from player1 import Agent

import torch.optim as optim


def get_state_in_json(player_score, high_score, head_pos, snake_pos, apple_pos, prev_direction: np.ndarray):
    food_above = int(head_pos[1] < apple_pos.y)
    food_below = int(head_pos[1] > apple_pos.y)
    food_left = int(head_pos[0] > apple_pos.x)
    food_right = int(head_pos[0] < apple_pos.x)

    danger_above = int(head_pos[1] < CELL_SIZE) or \
                   int(any([block.y - head_pos[1] == CELL_SIZE and block.x == head_pos[0] for _, block in enumerate(snake_pos) if _ > 1]))
    danger_below = int(head_pos[1] >= WINDOW_HEIGHT - CELL_SIZE) or \
                   int(any([head_pos[1] - block.y == CELL_SIZE and block.x == head_pos[0] for _, block in enumerate(snake_pos) if _ > 1]))
    danger_left = int(head_pos[0] < CELL_SIZE) or \
                  int(any([head_pos[0] - block.x == CELL_SIZE and block.y == head_pos[1] for _, block in enumerate(snake_pos) if _ > 1]))
    danger_right = int(head_pos[0] >= WINDOW_WIDTH - CELL_SIZE) or \
                   int(any([block.x - head_pos[0] == CELL_SIZE and block.y == head_pos[1] for _, block in enumerate(snake_pos) if _ > 1]))

    return \
        {"Player Score: ": player_score,
         "High Score: ": high_score,
         "Head Position: ": head_pos,
         "Snake Position: ": [(block.x, block.y) for block in snake_pos],
         "Apple Position: ": (apple_pos.x, apple_pos.y),
         "Previous Direction: ": str(prev_direction),
         "Moving Up": int((prev_direction == UP).all()),
         "Moving Down": int((prev_direction == DOWN).all()),
         "Moving Left": int((prev_direction == LEFT).all()),
         "Moving Right": int((prev_direction == RIGHT).all()),
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

    score_plot = []
    counter_plot = []

    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    SCORE = ScoreBoard()

    # Ready Player 1.
    player1 = Agent(params).to_device()
    player1.optimizer = optim.Adam(player1.parameters(), weight_decay=0, lr=params['learning_rate'])

    # Game counter initialize.
    game_number = 1
    while game_number < params['episodes']:

        # Мы всегда будем начинать игру с начала. После проигрыша сразу
        # начинается следующая.
        print(f"Episode {game_number} of {params['episodes']}")
        run_game(player1, game_number)

        if params['train']:
            player1.replay_new(player1.memory, params['batch_size'])

        score_plot.append(SCORE.player_score)
        counter_plot.append(game_number)
        mean = np.mean(score_plot)
        stdev = np.std(score_plot)
        # Increment game counter before start new game.
        game_number += 1

        if params['train']:
            model_weights = player1.state_dict()
            torch.save(model_weights, params["weights_path"])
        if params['plot_score']:
            SCORE.plot_seaborn(array_counter=counter_plot, array_score=score_plot, train=params['train'])
    print("Training complete!")


def run_game(agent, game_number):
    # создать яблоко в позиции (20, 10)
    apple = Apple(Cell(WINDOW_WIDTH / WIDTH * round(WIDTH/3), WINDOW_HEIGHT / HEIGHT * round(HEIGHT/2), DISPLAY))
    # создать змейку. Пусть она состоит из трех ячеек
    #  в строке 10 и столбцах 3, 4, 5.
    #  Какой тип данных удобен для представления змейки?
    snake = Snake(Cell(WINDOW_WIDTH / WIDTH * 4, WINDOW_HEIGHT / HEIGHT * round(HEIGHT/4), DISPLAY),
                  Cell(WINDOW_WIDTH / WIDTH * 3, WINDOW_HEIGHT / HEIGHT * round(HEIGHT/4), DISPLAY),
                  Cell(WINDOW_WIDTH / WIDTH * 2, WINDOW_HEIGHT / HEIGHT * round(HEIGHT/4), DISPLAY))

    # Reset player score.
    SCORE.player_score = 0

    # Initialize list containing tuples: (action, current state).
    action_state_list = []
    action_counter = 0

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

    steps = 0  # steps since the last positive reward
    while (not any((snake_hit_self(snake), snake_hit_edge(snake)))) and (steps < 100):
        # Before snake does its first move, assign action = 'None'.
        action_counter += 1
        action = 'none'
        # Previous snake direction. We'll use as one of the current state parameters for evaluation.
        snake_prev_direction = snake.direction

        if not params['train']:
            agent.epsilon = 0.01
        else:
            # agent.epsilon is set to give randomness to actions
            agent.epsilon = 1 - (game_number * params['epsilon_decay_linear'])

        # get previous environment state.
        state_old = get_state(
            get_state_in_json(player_score=SCORE.player_score,
                              high_score=SCORE.high_score,
                              head_pos=get_snake_new_head(snake),
                              snake_pos=snake.body,
                              apple_pos=apple.apple,
                              prev_direction=snake_prev_direction)
        )
        head_apple_distance_old_x, head_apple_distance_old_y = abs(get_snake_new_head(snake)[0] - apple.apple.x),\
                                                               abs(get_snake_new_head(snake)[1] - apple.apple.y)

        # perform random actions based on agent.epsilon, or choose the action
        if random.uniform(0, 1) < agent.epsilon:
            snake.turn(matrix=np.eye(3)[random.randint(0, 2)],
                       prev_direction=snake_prev_direction,
                       move_list=SNAKE_MOVE)
        else:
            # predict action based on the old state
            with torch.no_grad():
                state_old_tensor = torch.tensor(state_old.reshape((1, 12)), dtype=torch.float32).to(DEVICE)
                prediction = agent(state_old_tensor)
                snake.turn(matrix=np.eye(3)[np.argmax(prediction.detach().cpu().numpy()[0])],
                           prev_direction=snake_prev_direction,
                           move_list=SNAKE_MOVE)

        # сдвинуть змейку в заданном направлении
        snake.move()

        # обработайте ситуацию столкновения змейки с яблоком.
        #  В этом случае нужно:
        #  * Увеличить размер змейки
        #  * Создать новое яблоко.
        if snake_hit_apple(snake, apple):
            snake.grow()
            apple.spawn([(block.x, block.y) for block in snake.body])  # check apple does not spawn on snake.
            SCORE.score()

        # Calculate new environment state after snake moved.
        state_new = get_state(
            get_state_in_json(player_score=SCORE.player_score,
                              high_score=SCORE.high_score,
                              head_pos=get_snake_new_head(snake),
                              snake_pos=snake.body,
                              apple_pos=apple.apple,
                              prev_direction=snake_prev_direction)
        )
        head_apple_distance_new_x, head_apple_distance_new_y = abs(get_snake_new_head(snake)[0] - apple.apple.x),\
                                                               abs(get_snake_new_head(snake)[1] - apple.apple.y)

        # Set reward for the new state.
        reward = agent.set_reward(snake, apple, head_apple_distance_new_x, head_apple_distance_old_x,
                                  head_apple_distance_new_y, head_apple_distance_old_y)

        # If snake hit apple or moved towards it, reset steps counter to 0.
        if reward > 0:
            steps = 0

        if params['train']:
            # train short memory base on the new action and state
            agent.train_short_memory(state_old, snake.turn_direction, reward, state_new,
                                     any((snake_hit_self(snake), snake_hit_edge(snake))))
            # store the new data into a long term memory
            agent.remember(state_old, snake.turn_direction, reward, state_new,
                           any((snake_hit_self(snake), snake_hit_edge(snake))))

        # передать яблоко в функцию отрисовки кадра
        # передать змейку в функцию отрисовки кадра
        if params['display']:
            draw_frame(snake, apple, SCORE)
        FPS_CLOCK.tick(FPS)

        steps += 1

        # Appending the current action (could be 'none') and the current state of the snake to
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

    # если змейка задела свой хвост, завершить игру.
    #  Для проверки восппользуйтесь функцией snake_hit_self.
    if snake_hit_self(snake):
        write_state_to_file(STATE, CURRENT_TIME)


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
