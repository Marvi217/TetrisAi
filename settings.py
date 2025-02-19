import os
import sys
import pygame as pg


vec = pg.math.Vector2

FPS = 60
FIELD_COLOR = (48,39,32)
BG_COLOR = (24,89,117)

if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

SPRITE_DIR = os.path.join(base_path, 'sprites')
FONT_PATH = os.path.join(base_path, 'font', 'FREAKSOFNATUREMASSIVE.ttf')

ANIMATION_TIME = 30
FAST_ANIMATION = 2

TILE_SIZE = 40
FIELD_SIZE = FIELD_W, FIELD_H = 10,20
FIELD_RES = FIELD_W * TILE_SIZE, FIELD_H * TILE_SIZE
FIELD_OFFSET_X = 250

FIELD_SCALE_W, FIELD_SCALE_H = 2.4, 1
WIN_RES = WIN_W, WIN_H = FIELD_RES[0] * FIELD_SCALE_W, FIELD_RES[1] * FIELD_SCALE_H

POS_OFFSET = vec(FIELD_W // 2 - 1, 0)
NEXT_POS_OFFSET = vec(FIELD_W * 1.3, FIELD_H * 0.45)
HELD_POS_OFFSET = vec(FIELD_W * 0.3, FIELD_H * 0.25)
MOVE_DIRECTIONS = {'left': vec(-1,0), 'right': vec(1,0), 'down': vec(0,1)}

TETROMINOES = {
    'T': [(0, 0), (-1, 0), (1, 0), (0, -1)],
    'O': [(0, 0), (0, -1), (1, 0), (1, -1)],
    'J': [(0, 0), (-1, 0), (0, -1), (0, -2)],
    'L': [(0, 0), (1, 0), (0, -1), (0, -2)],
    'I': [(0, 0), (0, 1), (0, -1), (0, -2)],
    'S': [(0, 0), (-1, 0), (0, -1), (1, -1)],
    'Z': [(0, 0), (1, 0), (0, -1), (-1, -1)]
}