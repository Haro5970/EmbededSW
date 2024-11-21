import numpy as np
from Map import *
from Player import *
from Entity import *


class Camera:

    def __init__(self):
        self.size = (240, 240)
        self.pos = np.zeros(2)

    def view(self, player: Player, bg):
        view = bg.copy()  # size[0]*size[1]*3
        view[player.pos[0]:player[0] + player.size[0], player.pos[1]:player[1] + player.size[1]] = (0, 255, 0)
        for e in player.map.enemies:
            view[e.pos[0]:e.pos[0] + e.size[0], e.pos[1]:e.pos[1] + e.size[1]] = (255, 0, 0)

        view[player.hook.pos[0]:player.hook.pos[0] + player.hook.size[0],
        player.hook.pos[1]:player.hook.pos[1] + player.hook.size[1]] = (0, 0, 255)

        self.pos = player.pos - np.array([self.size[0] // 2, self.size[1] // 2])
        self.pos[0] = max(0, self.pos[0])
        self.pos[1] = max(0, self.pos[1])

        self.pos[0] = min(bg.shape[0] - self.size[0], self.pos[0])
        self.pos[1] = min(bg.shape[1] - self.size[1], self.pos[1])

        view = view[self.pos[0]:self.pos[0] + self.size[0], self.pos[1]:self.pos[1] + self.size[1]]

        return view

