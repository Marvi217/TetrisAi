import copy

import pygame.freetype as ft
from settings import *
from tetromino import Tetromino


class Text:
    def __init__(self, app):
        self.app = app
        self.font = ft.Font(FONT_PATH)

    def draw(self):
        window = FIELD_OFFSET_X *0.4
        self.font.render_to(self.app.screen, (window + WIN_W * 0.595, WIN_H * 0.02),
                            text='Tetris', fgcolor='white', size=TILE_SIZE * 1.65, bgcolor='black')
        self.font.render_to(self.app.screen, (window + WIN_W * 0.65, WIN_H * 0.22),
                            text='Next', fgcolor='white', size=TILE_SIZE * 1.4, bgcolor='black')
        self.font.render_to(self.app.screen, (window + WIN_W * 0.64, WIN_H * 0.67),
                            text='Score', fgcolor='white', size=TILE_SIZE * 1.4, bgcolor='black')
        self.font.render_to(self.app.screen, (window + WIN_W * 0.64, WIN_H * 0.8),
                            text=f'{self.app.tetris.score}', fgcolor='white', size=TILE_SIZE * 1.8)
        self.font.render_to(self.app.screen, (WIN_W * 0.04, WIN_H * 0.02),
                            text='Held', fgcolor='white', size=TILE_SIZE * 1.4, bgcolor='black')

class Tetris:
    def __init__(self, app):
        self.app = app
        self.sprite_group = pg.sprite.Group()
        self.field_array = self.get_field_array()
        self.tetromino = Tetromino(self)
        self.next_tetromino = Tetromino(self, current=False)
        self.held_tetromino = None
        self.held_used = False
        self.speed_up = False
        self.gameover = False
        self.reward = 0
        self.score = 0
        self.full_lines = 0
        self.points_per_level = {0: 0, 1: 1, 2: 3, 3: 7, 4: 15}

    def get_score(self):
        self.score += self.points_per_level[self.full_lines]
        self.full_lines = 0

    def get_avg_height(self):
        total_height = 0
        filled_columns = 0

        for x in range(FIELD_W):
            column_height = 0
            for y in range(FIELD_H):
                if self.field_array[y][x]:
                    column_height = FIELD_H - y
                    break
            if column_height > 0:
                total_height += column_height
                filled_columns += 1

        return total_height / filled_columns if filled_columns > 0 else 0

    def get_col_height(self, col):
        for y in range(FIELD_H):
            if self.field_array[y][col]:
                return FIELD_H - y
        return 0

    def calculate_bumpiness(self):
        bumpiness = 0
        prev_height = -1
        for c in range(FIELD_W):
            h = self.get_col_height(c)
            if prev_height != -1:
                bumpiness += abs(h - prev_height)
            prev_height = h
        return bumpiness

    def count_holes(self):
        holes = 0

        for x in range(FIELD_W):
            has_block_above = False
            for y in range(FIELD_H):
                if self.field_array[y][x]:
                    has_block_above = True
                elif has_block_above and not self.field_array[y][x]:
                    if y + 1 < FIELD_H and self.field_array[y + 1][x]:
                        if (y + 1 == FIELD_H - 1) or (y + 2 < FIELD_H and self.field_array[y + 2][x]):
                            holes += 1
                elif has_block_above and self.field_array[y][x]:
                    has_block_above = True

        return holes

    def put_tetromino_in_array(self):
        for block in self.tetromino.blocks:
            x, y = int(block.pos.x), int(block.pos.y)
            self.field_array[y][x] = block

    def get_field_array(self):
        return [[0 for x in range(FIELD_W)] for y in range(FIELD_H)]

    def is_gameover(self):
        return any(block.pos.y < 0 for block in self.tetromino.blocks)

    def chceck_tetromino_landing(self):
        if self.tetromino.landing:
            if self.is_gameover():
                self.gameover = True
            else:
                self.speed_up = False
                self.put_tetromino_in_array()
                self.next_tetromino.current = True
                self.tetromino = self.next_tetromino
                self.next_tetromino = Tetromino(self, current=False)
                self.held_used = False

    def hold_tetromino(self, ):
        if self.held_used:
            return
        if self.held_tetromino is None:
            self.held_tetromino = self.tetromino
            self.held_tetromino.held = True

            self.next_tetromino.current = True
            self.tetromino = self.next_tetromino
            self.next_tetromino = Tetromino(self, current=False)
        else:
            self.held_tetromino, self.tetromino, = self.tetromino, self.held_tetromino
            self.held_tetromino.held = True
            self.held_tetromino.current = False
            self.tetromino.held = False
            self.tetromino.current = True
            self.tetromino.reset_position()

        self.held_used = True

    def control(self, action):
        if action[0] == 1:  # Move left
            self.tetromino.move(direction='left')
        if action[1] == 1:  # Move right
            self.tetromino.move(direction='right')
        if action[2] == 1:  # Rotate
            self.tetromino.rotate()
        if action[3] == 1:  # Speed up
            self.speed_up = True
        if action[4] == 1:  # Hold
            self.hold_tetromino()

    def chceck_full_rows(self):
        row = FIELD_H - 1
        lines_cleared = 0
        for y in range(FIELD_H - 1, -1, -1):
            for x in range(FIELD_W):
                self.field_array[row][x] = self.field_array[y][x]

                if self.field_array[y][x]:
                    self.field_array[row][x].pos = vec(x, y)

            if sum(map(bool, self.field_array[y])) < FIELD_W:
                row -= 1
            else:
                for x in range(FIELD_W):
                    self.field_array[row][x].alive = False
                    self.field_array[row][x] = 0

                lines_cleared += 1
        self.full_lines += lines_cleared
        return lines_cleared

    def reset(self):
        self.sprite_group = pg.sprite.Group()
        self.field_array = self.get_field_array()
        self.tetromino = Tetromino(self)
        self.next_tetromino = Tetromino(self, current=False)
        self.held_tetromino = None
        self.held_used = False
        self.speed_up = False
        self.gameover = False
        self.reward = 0
        self.score = 0
        self.full_lines = 0

    def update(self):
        trigger = [self.app.anim_trigger, self.app.fast_anim_trigger][self.speed_up]

        if trigger:
            x = self.chceck_full_rows()
            match x:
                case 1:
                    self.reward += 2000000
                    print(f"Nagroda za 1 wypełniony wiersz: {self.reward}")
                case 2:
                    self.reward += 4000000
                    print(f"Nagroda za 2 wypełnione wiersze: {self.reward}")
                case 3:
                    self.reward += 8000000
                    print(f"Nagroda za 3 wypełnione wiersze: {self.reward}")
                case 4:
                    self.reward += 15000000
                    print(f"Nagroda za 4 wypełnione wiersze: {self.reward}")

            self.tetromino.update()
            self.chceck_tetromino_landing()
            self.get_score()

        self.sprite_group.update()

        if self.gameover:
            self.reward += self.analyze_field_after_game_over()
            self.reward -= 50  # Ograniczona kara za przegraną

        return self.score, self.gameover, self.reward

    def analyze_field_after_game_over(self):
        reward = 0
        print('Reward: ', reward, '\n')

        # Nagroda za bloki w poziomach 1-4
        for y in range(FIELD_H):
            for x in range(FIELD_W):
                if self.field_array[y][x]:
                    if y == 0:  # Poziom 1
                        reward += 50
                    elif y == 1:  # Poziom 2
                        reward += 50
                    elif y == 2:  # Poziom 3
                        reward += 50
                    elif y == 3:  # Poziom 4
                        reward += 50
                    elif y == 4:  # Poziom 5
                        reward += 40
                    elif y == 5:  # Poziom 6
                        reward += 30
                    elif y == 6:  # Poziom 7
                        reward += 20
                    elif y == 7:  # Poziom 8
                        reward += 10
                    elif y == 8:  # Poziom 9
                        reward += 50
                    elif y >= 9:  # Poziom 10 i wyżej
                        penalty = max(-1, -(y - 9) * 10)  # Zaczyna od -10, zwiększa do -100 dla poziomu 20
                        reward += penalty

        print(f"Nagroda za bloki w poziomach: {reward}")
        print('Reward: ', reward, '\n')

        # Liczba otworów
        holes = self.count_holes()
        if holes > 5:
            reward -= (100 * holes)  # Kara za otwory
            print(f"Kara za otwory: {-100 * holes}")

        print('Reward: ', reward, '\n')

        # Liczba wypełnionych poziomów
        filled_levels = sum(1 for y in range(FIELD_H) if all(self.field_array[y][x] for x in range(FIELD_W)))
        if filled_levels > 7:
            blocks_in_filled_levels = filled_levels * FIELD_W  # Liczba bloków w pełnych poziomach
            reward += blocks_in_filled_levels * 100  # Nagroda za każdy blok w tych poziomach
            print(f"Nagroda za pełne poziomy: {blocks_in_filled_levels * 100}")
        elif filled_levels < 4:
            penalty_for_filled_levels = (4 - filled_levels) * 200  # Kara za brakujące poziomy
            reward -= penalty_for_filled_levels
            print(f"Kara za brakujące poziomy: {-penalty_for_filled_levels}")

        print('Reward: ', reward, '\n')

        return reward

    def draw_grid(self):
        for x in range(FIELD_W):
            for y in range(FIELD_H):
                pg.draw.rect(self.app.screen, 'black',
                             ((x * TILE_SIZE) + FIELD_OFFSET_X, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

    def draw(self):
        self.draw_grid()
        self.sprite_group.draw(self.app.screen)
