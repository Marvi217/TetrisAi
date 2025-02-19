from settings import *
import random

class Block(pg.sprite.Sprite):
    def __init__(self, tetromino, pos):
        self.tetromino = tetromino
        self.pos = vec(pos) + POS_OFFSET
        self.next_pos = vec(pos) + NEXT_POS_OFFSET
        self.held_pos = vec(pos) + HELD_POS_OFFSET
        self.alive = True

        super().__init__(tetromino.tetris.sprite_group)
        self.image = tetromino.image
        self.rect = self.image.get_rect()

    def is_alive(self):
        if not self.alive:
            self.kill()

    def rotate(self, pivot_pos):
        translated = self.pos - pivot_pos
        rotated = translated.rotate(90)
        return rotated + pivot_pos

    def set_rect_pos(self):
        if self.tetromino.held:
            pos = self.held_pos
            self.rect.topleft = (pos.x * TILE_SIZE, pos.y * TILE_SIZE)
            return
        elif self.tetromino.current:
            pos = self.pos
        else:
            pos = self.next_pos

        self.rect.topleft = (pos.x * TILE_SIZE + FIELD_OFFSET_X, pos.y * TILE_SIZE)

    def update(self):
        self.is_alive()
        self.set_rect_pos()

    def is_collide(self, pos):
        x, y = int(pos.x), int(pos.y)
        if 0 <= x < FIELD_W and y < FIELD_H and (
                y < 0 or not self.tetromino.tetris.field_array[y][x]):
            return False
        return True

class Tetromino:
    def __init__(self, tetris, held=False, current = True):
        self.tetris = tetris
        self.shape = random.choice(list(TETROMINOES.keys()))
        self.image = random.choice(tetris.app.img)
        self.blocks = [Block(self, pos) for pos in TETROMINOES[self.shape]]
        self.pos = vec(TETROMINOES[self.shape][0]) + POS_OFFSET
        self.landing = False
        self.current  = current
        self.held = held

    def rotate(self):
        pivot_pos = self.blocks[0].pos

        if self.blocks[0].tetromino.shape != 'O':
            new_block_pos = [block.rotate(pivot_pos) for block in self.blocks]
        else:
            new_block_pos = [block.pos for block in self.blocks]

        if not self.is_collide(new_block_pos):
            for i, block in enumerate(self.blocks):
                block.pos = new_block_pos[i]

    def calculate_landing_position(self):
        new_blocks = [Block(self, block.pos.copy()) for block in self.blocks]
        while True:
            new_block_pos = [block.pos + vec(0, 1) for block in new_blocks]
            if self.is_collide(new_block_pos):
                break
            for i, block in enumerate(new_blocks):
                block.pos = new_block_pos[i]

        return new_blocks

    def can_move(self, dx, dy):
        for block in self.blocks:
            new_x = int(block.pos.x + dx)
            new_y = int(block.pos.y + dy)

            # Sprawdź, czy nowe położenie jest w granicach planszy
            if new_x < 0 or new_x >= FIELD_W or new_y >= FIELD_H:
                return False

            # Sprawdź kolizję z innymi blokami
            if new_y >= 0 and self.tetris.field_array[new_y][new_x]:
                return False

        return True

    def destroy(self):
        for block in self.blocks:
            block.alive = False
        block.kill()

    def reset_position(self):
        for i, block in enumerate(self.blocks):
            block.pos = vec(TETROMINOES[self.shape][i]) + POS_OFFSET

    def is_collide(self, block_pos):
        return any(map(Block.is_collide, self.blocks, block_pos))

    def move(self, direction):
        move_direction = MOVE_DIRECTIONS[direction]
        new_block_pos = [block.pos + move_direction for block in self.blocks]
        is_collide = self.is_collide(new_block_pos)

        if not is_collide:
            for block in self.blocks:
                block.pos += move_direction
        elif direction == 'down':
            self.landing = True
    def update(self):
        self.move(direction='down')
