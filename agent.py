import torch
import random
import numpy as np
from collections import deque
from main import AppAi
from model import Linear_QNet, QTrainer
from helper import plot
from settings import *

MAX_MEMORY = 100000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.number_of_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(245, 650, 650, 5)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        field = game.tetris.field_array
        current_tetromino = game.tetris.tetromino
        next_tetromino = game.tetris.next_tetromino

        state = []

        # 1. Plansza - 0 jeśli puste, 1 jeśli blok
        for row in field:
            state.extend([1 if block else 0 for block in row])

        # 2. Wysokości kolumn
        col_heights = [game.tetris.get_col_height(col) for col in range(FIELD_W)]
        state.extend(col_heights)

        # 3. Wyboistość (bumpiness)
        state.append(game.tetris.calculate_bumpiness())

        # 4. Liczba dziur
        holes = game.tetris.count_holes()
        state.append(holes)

        # 5. Stosunek dziur do wysokości planszy (nowa cecha)
        avg_height = sum(col_heights) / FIELD_W
        state.append(holes / avg_height if avg_height > 0 else 0)

        # 6. Najwyższy filar (nowa cecha)
        highest_col = max(col_heights)
        state.append(highest_col)

        # 7. Różnica między najwyższą a najniższą kolumną (nowa cecha)
        state.append(highest_col - min(col_heights))

        # 8. Liczba bloków poniżej wysokości 6
        blocks_below_six = sum(
            1 for x in range(FIELD_W) for y in range(FIELD_H) if game.tetris.field_array[y][x] and y >= 6
        )
        state.append(blocks_below_six)

        # 9. Pozycja tetromino
        state.append(int(current_tetromino.pos.x))
        state.append(int(current_tetromino.pos.y))

        # 10. Kształt aktualnego i następnego tetromino (one-hot encoding)
        shape_index = self.get_shape_index(current_tetromino.shape)
        next_shape_index = self.get_shape_index(next_tetromino.shape)

        shape_one_hot = [0] * 7
        shape_one_hot[shape_index] = 1
        state.extend(shape_one_hot)

        next_shape_one_hot = [0] * 7
        next_shape_one_hot[next_shape_index] = 1
        state.extend(next_shape_one_hot)

        # 11. Liczba prawie pełnych rzędów (brakuje od 1 do FIELD_W - 1 bloków do wypełnienia)
        almost_full_rows_counts = [0] * (FIELD_W - 1)  # Lista dla równań brakujących 1 do FIELD_W - 1 bloków

        for y in range(FIELD_H):
            filled_blocks = sum(map(bool, field[y]))  # Zliczanie wypełnionych bloków w wierszu
            if filled_blocks > 0 and filled_blocks < FIELD_W:
                almost_full_rows_counts[filled_blocks - 1] += 1  # Zwiększamy licznik dla brakujących bloków

        # Dodajemy wyniki do stanu
        state.extend(almost_full_rows_counts)

        # 12. Najwyższy punkt na planszy
        highest_point = min((y for y in range(FIELD_H) if any(field[y][x] for x in range(FIELD_W))), default=FIELD_H)
        state.append(highest_point)

        # 13. Liczba dostępnych ruchów w poziomie (bez kolizji)
        move_options = sum(1 for dx in range(-FIELD_W, FIELD_W) if current_tetromino.can_move(dx, 0))
        state.append(move_options)

        # 14. Średnia wysokość kolumn
        state.append(avg_height)

        # 15. Liczba pustych miejsc wokół aktualnego tetromino (nowa cecha)
        free_spaces = sum(
            1 for dx in [-1, 1] for dy in [-1, 1]
            if 0 <= current_tetromino.pos.x + dx < FIELD_W
            and 0 <= int(current_tetromino.pos.y + dy) < FIELD_H
            and not field[int(current_tetromino.pos.y + dy)][int(current_tetromino.pos.x + dx)]
        )
        state.append(free_spaces)

        return np.array(state, dtype=float)  # Zamieniłem na float, bo są wartości dziesiętne

    def get_shape_index(self, shape):
        shape_mapping = {'T': 0, 'O': 1, 'J': 2, 'L': 3, 'I': 4, 'S': 5, 'Z': 6}
        return shape_mapping.get(shape, -1)

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))

    def train_short_mem(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def train_long_mem(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, game_overs = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def get_action(self, state):
        self.epsilon = max(5, 50 - self.number_of_games)
        final_move = [0, 0, 0, 0, 0]

        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 4)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

def train():
    plot_scores = []
    plot_avg_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = AppAi()

    while True:
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)
        reward, game_over, score = game.play_step(final_move)
        state_new = agent.get_state(game)
        agent.train_short_mem(state_old, final_move, reward, state_new, game_over)
        agent.remember(state_old, final_move, reward, state_new, game_over)
        if game_over:
            game.tetris.reset()
            agent.number_of_games += 1
            agent.train_long_mem()
            if score > record:
                record = score
                agent.model.save()
            print('Gra: ', agent.number_of_games, ', Wynik: ', score, ' Nagroda: ', reward, ' Rekord: ', record)
            print("Gra skończona\n--------------------------------------------------------------------------------------")
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.number_of_games
            plot_avg_scores.append(mean_score)
            plot(plot_scores, plot_avg_scores)

if __name__ == '__main__':
    train()
