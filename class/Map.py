import json

import numpy as np
from PIL import Image, ImageDraw
from Entity import *


class Block:

    def __init__(self, pos: tuple, size: tuple, color: tuple, effect: int = 0):
        self.pos = pos
        self.size = size
        self.color = color

        self.effect = effect

        image = Image.new('RGB', self.size, (0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((0, 0, self.size[0] - 1, self.size[1] - 1), outline=self.color, width=1, radius=5)
        self.image = np.array(image)

    def getForCollide(self):
        return self.pos[0], self.pos[1], self.size[0], self.size[1]


class Map:

    def __init__(self, map_file_name: str):
        with open(map_file_name, 'r', encoding="utf8") as f:
            data = json.load(f)
        self.tile_map: tuple = data["tile_map"]
        self.size = tuple([len(self.tile_map[0]), len(self.tile_map[1])])

        self.playerStartPos = data["playerStartPos"]

        self.block_size = (20, 20)
        self.blocks = []
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self.tile_map[i][j] != 0:
                    self.blocks.append(
                        Block((i * 20, j * 20), self.block_size, (255, 255, 255), self.tile_map[i][j])
                    )

        self.enemyData = data["enemies"]
        self.enemies = []

    def getBG(self):
        bg = np.zeros((self.size[0] * self.block_size[0], self.size[1] * self.block_size[1], 3), dtype='uint8')
        for block in self.blocks:
            bg[block.pos[0]:block.pos[0] + block.size[0], block.pos[1]:block.pos[1] + block.size[1]] = block.image

        return bg
