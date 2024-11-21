from Map import *
import numpy as np


class Entity:

    def __init__(self, pos: list, map):
        self.pos = np.array(pos, dtype='float64')
        self.vel = np.zeros(2, dtype='float64')
        self.map = map

        self.speed = (1, 3)
        self.frac = 0.1
        self.size = np.zeros(2)  # 실제 사이즈는 x2+1

        self.heading = 1  # 1:right / -1:left

    def checkCollision(self):
        returnBox = [0, 0, 0, 0, []]
        for block in self.map.blocks:
            if np.linalg.norm(block.pos - block.pos) > 100:
                continue
            direction = self.collideWith(block)
            if direction:
                if direction == "top":
                    self.vel[1] = 0
                    self.pos[1] = block.pos[1] - self.size[1]
                    returnBox[0] = 1
                elif direction == "bottom":
                    self.vel[1] = 0
                    self.pos[1] = block.pos[1] + self.size[1]
                    returnBox[1] = 1
                elif direction == "left":
                    self.vel[0] = 0
                    self.pos[0] = block.pos[0] - self.size[0]
                    returnBox[2] = 1
                elif direction == "right":
                    self.vel[0] = 0
                    self.pos[0] = block.pos[0] + self.size[0]
                    returnBox[3] = 1

                returnBox[4].append(block.effect)

        return returnBox

    def collideWith(self, other):  # other x,y,w,h
        next_pos = self.pos + self.vel
        left, right = next_pos[0] - self.size[0], next_pos[0] + self.size[0]
        top, bottom = next_pos[1] - self.size[1], next_pos[1] + self.size[1]
        other_left, other_right = other[0], other[0] + other[2]
        other_top, other_bottom = other[1], other[1] + other[3]

        if right > other_left and left < other_right:
            if bottom > other_top and top < other_bottom:
                distances = {
                    "top": abs(bottom - other_top),
                    "bottom": abs(top - other_bottom),
                    "left": abs(right - other_left),
                    "right": abs(left - other_right),
                }
                return min(distances, key=distances.get)
        return None

    def move(self):
        # 상속 받은 클래스에서 구현
        pass
