from typing import List
import numpy as np
import math
import json
from PIL import Image, ImageDraw, ImageOps
import pygame as pg
import random


class Entity:
    def __init__(self, pos, size, img_code):
        self.pos = np.array(pos, dtype="float64")  # 좌상단 꼭지점
        self.size = np.array(size, dtype="float64")
        self.vel = np.zeros(2, dtype="float64")
        self.image = img_code

    def collision(self, other):  # 0: no collision, 1: top, 2: bottom, 3: left, 4: right
        next_pos = self.pos + self.vel

        self_left, self_right = next_pos[0], next_pos[0] + self.size[0]
        self_top, self_bottom = next_pos[1], next_pos[1] + self.size[1]
        other_left, other_right = other.pos[0], other.pos[0] + other.size[0]
        other_top, other_bottom = other.pos[1], other.pos[1] + other.size[1]

        if self_right > other_left and self_left < other_right:
            if self_bottom > other_top and self_top < other_bottom:
                distances = {
                    1: abs(self_bottom - other_top),  # top
                    2: abs(self_top - other_bottom),  # bottom
                    3: abs(self_right - other_left) + 1,  # left
                    4: abs(self_left - other_right) + 1,  # right
                }
                return min(distances, key=distances.get)
        return 0


class Block(Entity):
    def __init__(self, pos, size, img_code, effect):
        super().__init__(pos, size, img_code)
        self.effect = effect


class Door(Entity):
    def __init__(self, pos, size, img_code):
        super().__init__(pos, size, img_code)
        self.isOpened = False

class Hook(Entity):
    def __init__(self, pos, img_code):
        super().__init__(pos, [10, 10], img_code)
        self.speed = 5

        self.angle = 0
        self.isShooting = 0
        self.isStuck = 0
        self.isPulling = 0
        self.target = None

        self.player = None

    def shoot(self, pos):
        if self.isShooting == 0:
            self.pos = pos.copy()
            self.isShooting = 1
            self.vel[0] = self.speed * math.cos(math.radians(self.angle))
            self.vel[1] = self.speed * math.sin(math.radians(self.angle))
        if self.isStuck == 1:
            self.setFree()

    def setFree(self):
        self.isShooting = 0
        self.isStuck = 0
        self.target = None

    def pull(self, player):
        if self.isStuck == 1:
            if type(self.target) == Block:
                vel = self.pos - player.pos
                abs_ = np.linalg.norm(vel)
                if abs_ == 0:
                    player.vel = np.zeros(2, dtype='float64')
                else:
                    vel = vel / abs_
                    player.vel = vel * player.hookPullSpeed


        else:
            if self.isShooting == 1:
                self.isPulling = 1
                self.vel = self.pos - player.pos
                abs = np.linalg.norm(self.vel)
                if abs == 0:
                    self.vel = np.zeros(2, dtype='float64')
                else:
                    self.vel = self.vel / abs
                    self.vel = -self.vel * self.speed

    def move(self, blocks, enemies, player):
        if self.isShooting:
            self.checkCollision(blocks, enemies, player)

        if not self.isStuck:
            self.pos += self.vel
        else:
            if type(self.target) == Enemy:
                self.pos = self.target.pos + self.target.size / 2 - self.size / 2

    def rotate(self, playerHeading):
        if not self.isStuck and not self.isShooting:
            self.angle += 6 * playerHeading
            self.angle %= 360

    def toPos(self, x, y):
        if not self.isStuck and not self.isShooting:
            self.pos = np.array([x, y], dtype="float64") - self.size / 2

    def checkCollision(self, blocks, enemies, player):
        for block in blocks:
            collision = self.collision(block)
            if collision:
                if collision == 1:
                    self.pos[1] = block.pos[1] - self.size[1]
                if collision == 2:
                    self.pos[1] = block.pos[1] + block.size[1]
                if collision == 3:
                    self.pos[0] = block.pos[0] - self.size[0]
                if collision == 4:
                    self.pos[0] = block.pos[0] + block.size[0]

                if block.effect == 2:
                    self.pull(player)
                else:
                    self.isShooting = 0
                    self.isStuck = 1
                    self.target = block

        for enemy in enemies:
            collision = self.collision(enemy)
            if collision:
                self.isShooting = 0
                self.isStuck = 1
                self.target = enemy
                enemy.attacked()

        if self.isPulling:
            playerCollision = self.collision(player)
            if playerCollision:
                self.isPulling = 0
                self.setFree()


class Player(Entity):
    def __init__(self, pos, img_code, hook: Hook, door: Door):
        super().__init__(pos, [10, 16], img_code)
        self.speed = (1, 3)
        self.frac = 0.1
        self.GA = 0.1

        self.heading = 1
        self.isAttacked = 0
        self.isJumping = 0

        self.hook = hook
        self.hookPullSpeed = 4

        self.door = door

    def goLeft(self):
        if self.isAttacked == 0:
            self.vel[0] = -self.speed[0]
            self.heading = -1

    def goRight(self):
        if self.isAttacked == 0:
            self.vel[0] = self.speed[0]
            self.heading = 1

    def jump(self):
        if self.isJumping == 0:
            self.vel[1] = -self.speed[1]
            self.isJumping = 1

    def shot(self):
        if self.isAttacked == 0:
            self.hook.shoot(self.pos)

    def pull(self):
        if self.isAttacked == 0:
            self.hook.pull(self)

    def attack(self, enemy):
        enemy.attacked()

    def attacked(self, enemy):
        self.isAttacked = 20
        isleft = self.pos[0] - enemy.pos[0] > 0  # enemy가 왼쪽에 있는지
        self.vel[0] = 2 if isleft else -2
        self.vel[1] = -2

    def checkCollision(self, blocks, enemies):
        self.isJumping = 1
        for block in blocks:
            collision = self.collision(block)
            if collision:
                if collision == 1:
                    self.vel[1] = 0
                    self.pos[1] = block.pos[1] - self.size[1]
                    self.isJumping = 0
                elif collision == 2:
                    self.vel[1] = 0
                    self.pos[1] = block.pos[1] + block.size[1]
                elif collision == 3:
                    self.vel[0] = 0
                    self.pos[0] = block.pos[0] - self.size[0]
                elif collision == 4:
                    self.vel[0] = 0
                    self.pos[0] = block.pos[0] + block.size[0]

        for enemy in enemies:
            collision = self.collision(enemy)
            if collision:
                if enemy.isDead:
                    print("Player eat Enemy")
                    enemies.remove(enemy)
                    self.hook.setFree()
                else:
                    self.attacked(enemy)

        doorCollision = self.collision(self.door)
        if doorCollision:
            # 모든 Enemy가 죽었으면
            if len(enemies) == 0:
                self.door.isOpened = True

    def move(self, blocks, enemies):
        self.checkCollision(blocks, enemies)

        if self.isAttacked > 0:
            self.isAttacked -= 1

        self.pos += self.vel
        self.vel[1] += self.GA
        self.vel[0] *= self.frac
        if abs(self.vel[0]) < 0.1:
            self.vel[0] = 0

        # Hook Spin
        self.hook.rotate(self.heading)
        center = self.pos + self.size / 2
        x = center[0] + 12 * math.cos(math.radians(self.hook.angle))
        y = center[1] + 12 * math.sin(math.radians(self.hook.angle))

        self.hook.toPos(x, y)


class Enemy(Entity):
    def __init__(self, pos, img_code, player, targetingWay):
        super().__init__(pos, [10, 18], img_code)
        self.speed = (0.3, 0.3)
        self.frac = 0.1
        self.GA = 0.1

        self.heading = -1

        self.isDead = False
        self.player = player

        self.targetingFunc = targetingWay

    def checkCollision(self, blocks):
        if self.isDead:
            return
        for block in blocks:
            collision = self.collision(block)
            if collision:
                if collision == 1:
                    self.vel[1] = 0
                    self.pos[1] = block.pos[1] - self.size[1]
                elif collision == 2:
                    self.vel[1] = 0
                    self.pos[1] = block.pos[1] + block.size[1]
                elif collision == 3:
                    self.vel[0] = 0
                    self.pos[0] = block.pos[0] - self.size[0]
                    if self.targetingFunc == 1:
                        self.heading = -1
                elif collision == 4:
                    self.vel[0] = 0
                    self.pos[0] = block.pos[0] + block.size[0]
                    if self.targetingFunc == 1:
                        self.heading = 1

    def move(self, blocks):
        self.checkCollision(blocks)

        if self.isDead:
            # 플레이어 방향으로 빠르게 이동
            vel = self.player.pos - self.pos
            abs_ = np.linalg.norm(vel)
            if abs_ == 0:
                self.vel = np.zeros(2, dtype='float64')
            else:
                vel = vel / abs_
                self.vel = vel * self.speed[0] * 15
            self.pos += self.vel
        else:
            self.pos += self.vel
            self.vel[1] += self.GA
            self.vel[0] *= self.frac
            if abs(self.vel[0]) < 0.1:
                self.vel[0] = 0

    def attacked(self):
        self.isDead = True

    def player_targeting(self):
        if self.targetingFunc == 0:
            pos = self.player.pos
            # player와의 거리가 100 이하일 때
            if np.linalg.norm(pos - self.pos) < 100:
                self.vel[0] = pos[0] - self.pos[0]
                abs_ = abs(self.vel[0])
                if abs_ == 0:
                    self.vel[0] = 0
                else:
                    self.vel[0] = self.vel[0] / abs_
                    self.vel[0] = self.vel[0] * self.speed[0]
        else:
            self.vel[0] = self.heading * self.speed[0]


class Map:
    def __init__(self, map_name):
        with open(map_name, "r", encoding='utf8') as f:
            map = json.load(f)
        tileMap = map["tileMap"]
        self.mapSize = [len(tileMap) * 20, len(tileMap[0]) * 20]
        self.blockList: List["Block"] = []
        for y in range(len(tileMap)):
            for x in range(len(tileMap[y])):
                if tileMap[x][y] != 0:
                    self.blockList.append(
                        Block([x * 20, y * 20],
                              [20, 20], "b" + str(tileMap[x][y]), tileMap[x][y]))
        self.door = Door(map["doorPos"], [20,40], "d")
        self.player = Player(
            map["playerStartPos"],
            "p",
            Hook([0, 0], "h"),
            self.door
        )
        self.player.hook.player = self.player

        self.enemyList = [Enemy(e[:2], "e", self.player, e[2]) for e in map["enemies"]]

        self.imageCodeTable = {}

        self.GameState = 0 # 0: 게임중, 1: 게임오버 2: 게임클리어

    def MakeImageCode(self):
        # 각 이미지 RGBA 로 로드
        self.imageCodeTable["p"] = Image.open("player.png").convert("RGBA")
        self.imageCodeTable["b1"] = Image.open("block1.png").convert("RGBA")
        self.imageCodeTable["b2"] = Image.open("block2.png").convert("RGBA")
        self.imageCodeTable["e"] = Image.open("enemy.png").convert("RGBA")
        self.imageCodeTable["h"] = Image.open("hook.png").convert("RGBA")
        self.imageCodeTable["d"] = Image.open("door.png").convert("RGBA")

    def getView(self):
        view = Image.new("RGB", self.mapSize, (0, 0, 0))
        draw = ImageDraw.Draw(view)

        cameraPos = self.player.pos - np.array([120, 120])
        cameraPos[0] = max(0, min(cameraPos[0], self.mapSize[0] - 240))
        cameraPos[1] = max(0, min(cameraPos[1], self.mapSize[1] - 240))

        for block in self.blockList:
            # 화면에 안나오는 블럭 pass
            if block.pos[0] > cameraPos[0] + 240 or block.pos[0] + block.size[0] < cameraPos[0] or block.pos[1] > \
                    cameraPos[1] + 240 or block.pos[1] + block.size[1] < cameraPos[1]:
                pass
            else:
                view.paste(self.imageCodeTable[block.image],
                           [int(w) for w in block.pos],
                           self.imageCodeTable[block.image]
                           )

        view.paste(
            self.imageCodeTable[self.door.image],
            [int(w) for w in self.door.pos],
            self.imageCodeTable[self.door.image]
        )

        for enemy in self.enemyList:
            # 화면에 안나오는 적 pass
            if enemy.pos[0] > cameraPos[0] + 240 or enemy.pos[0] + enemy.size[0] < cameraPos[0] or enemy.pos[1] > \
                    cameraPos[1] + 240 or enemy.pos[1] + enemy.size[1] < cameraPos[1]:
                pass
            else:
                view.paste(self.imageCodeTable[enemy.image],
                           [int(w) for w in enemy.pos],
                           self.imageCodeTable[enemy.image])

        view.paste(self.imageCodeTable[self.player.image],
                   [int(w) for w in self.player.pos],
                   self.imageCodeTable[self.player.image])

        hook = self.player.hook
        draw.line([int(w) for w in self.player.pos + self.player.size / 2] + [int(w) for w in hook.pos + hook.size / 2],
                  fill=(200, 200, 200), width=3)

        # hook 돌려서 붙이기
        hookimg = self.imageCodeTable[hook.image].rotate(-hook.angle)
        view.paste(hookimg,
                   [int(w) for w in hook.pos],
                   hookimg)

        view = view.crop((int(cameraPos[0]), int(cameraPos[1]), int(cameraPos[0] + 240), int(cameraPos[1] + 240)))
        view = ImageOps.mirror(view)
        view = view.rotate(90)
        return view

    def inputKey(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_l:
                    self.player.jump()
                elif event.key == pg.K_p:
                    self.player.shot()

        getKey = pg.key.get_pressed()
        if getKey[pg.K_a]:
            self.player.goLeft()
        elif getKey[pg.K_d]:
            self.player.goRight()
        elif getKey[pg.K_s]:
            self.player.pull()

    def step(self):
        self.inputKey()
        self.player.move(self.blockList, self.enemyList)
        for enemy in self.enemyList:
            enemy.player_targeting()
            enemy.move(self.blockList)
        self.player.hook.move(self.blockList, self.enemyList, self.player)

        return self.door.isOpened

    def draw(self, screen):
        view = self.getView()
        surface = pg.surfarray.make_surface(np.array(view))
        screen.blit(surface, (0, 0))

        font = pg.font.SysFont("arial", 10)
        text = font.render(f'Pos: {[int(w) for w in self.player.hook.pos]}'
                           f'   Vel: {self.player.hook.vel}'
                           f'    IsJumping: {self.player.isJumping}'
                           f'   IsAttacked: {self.player.isAttacked}'
                           , True, (255, 255, 255))
        surface.blit(text, (0, 0))
        text = font.render(
            f'HAngle: {self.player.hook.angle} / target: {type(self.player.hook.target)} / isShooting: {self.player.hook.isShooting}   isStuck: {self.player.hook.isStuck}',
            True, (255, 255, 255))
        surface.blit(text, (0, 20))
        screen.blit(surface, (0, 0))


map = Map("map.json")
map.MakeImageCode()
pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode((240, 240))

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    map.step()
    map.step()
    map.step()
    running = not map.step()
    map.draw(screen)
    pg.display.flip()
    clock.tick(15)
