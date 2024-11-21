import math
from Entity import *
import numpy as np
from Map import *


class Hook(Entity):
    def __init__(self, pos, map, player):
        super().__init__(pos, map)
        self.size = np.array([2, 2])

        self.theta = 0

        self.max_len = 300
        self.isStuck = False
        self.owner: Player = player

        self.target = None

    def thrown(self, force):
        self.vel[0] = math.cos(math.radians(self.theta))
        self.vel[1] = math.sin(math.radians(self.theta))
        self.vel *= force

    def pulled(self):
        if self.isStuck:
            if type(self.target) == Block:
                # owner를 self.pox로 이동
                self.owner.vel = self.pos - self.owner.pos
                self.owner.vel = self.owner.vel / np.linalg.norm(self.owner.vel) * 1
            else:
                # target을 owner.pos로 이동
                self.target.vel = self.owner.pos - self.target.pos
                self.target.vel = self.target.vel / np.linalg.norm(self.target.vel) * 1
        else:
            # 잡은게 없을경우 self를 owner로 이동
            self.vel = self.owner.pos - self.pos
            self.vel = self.vel / np.linalg.norm(self.vel) * 1

    def checkCollision(self):
        returnBox = super().checkCollision()
        if returnBox[0] == 1 or returnBox[1] == 1 or returnBox[2] == 1 or returnBox[3] == 1:
            self.vel = np.zeros(2)
            self.isStuck = True

        # 다른 Entity와 충돌 체크
        checkEntities = [e for e in self.map.enemies if np.linalg.norm(e.pos - self.pos) < 100]
        for e in checkEntities:
            box = [e.pos[0], e.pos[1], e.pos + e.size[0], e.pos + e.size[1]]
            col = self.collideWith(box)
            if col is not None:
                self.isStuck = True
                self.target = e


class Player(Entity):

    def __init__(self, pos: list, map: Map):
        super().__init__(pos, map)
        self.size = np.array([5, 8])

        self.hook = Hook(self.pos, map, self)
        self.onGround = 0
        self.isAttacked = 0

    def checkCollision(self):
        # block check
        returnBox = super().checkCollision()  # t/b/l/r / E
        self.onGround = returnBox[0]

        # enemy check
        checkEnemies = [e for e in self.map.enemies
                        if np.linalg.norm(e.pos - self.pos) < 100]
        for e in checkEnemies:
            box = [e.pos[0],
                   e.pos[1],
                   e.pos + e.size[0],
                   e.pos + e.size[1]]
            col = self.collideWith(box)
            if col is not None:
                if col == "top":
                    print("Attack")
                    self.map.enemies.remove(e)
                else:
                    print("Attacked")
                    if col == "left":
                        self.vel = np.array([-2, 2], dtype="float64")
                    elif col == "right":
                        self.vel = np.array([2, -2], dtype="float64")

                    self.isAttacked = 20

        return returnBox

    def throwHook(self):
        self.hook.thrown(10)

    def pullHook(self):
        self.hook.pulled()

    def goRight(self):
        if self.isAttacked == 0:
            self.vel[0] = self.speed[0]
            self.heading = 1

    def goLeft(self):
        if self.isAttacked == 0:
            self.vel[0] = -self.speed[0]
            self.heading = -1

    def jump(self):
        if self.onGround and self.isAttacked == 0:
            self.vel[1] = -self.speed[1]

    def move(self):
        if self.isAttacked > 0:
            self.isAttacked -= 1

        if self.isAttacked == 0:
            self.vel[0] *= self.frac
            self.vel[1] += 0.1

        self.checkCollision()

        self.pos += self.vel
