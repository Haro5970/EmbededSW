import math

from PIL import Image
import json
import numpy
from typing import List


class Player:
    def __init__(self, map, enemies: List["Enemy"]):
        self.pos = numpy.zeros(2)  # center position
        self.vel = numpy.zeros(2)

        self.onGround = 0
        self.speed = (1, 3)
        self.frac = 0.1
        self.size = numpy.array([5, 8])  # half width and half height

        self.theta = 0

        self.direction = 1

        self.target = [0]
        self.target_vel = numpy.zeros(2)

        self.map = map
        self.enemies = enemies
        self.isAttacked = 0

        self.debug = ""

    def move(self):
        self.onGround = 0  # Reset ground state each frame
        self.debug = ''
        # 블럭 충돌 확인 및 위치 보정
        for block in self.map.blocks:
            collide = self.colide_with(block)
            if collide == "top":
                self.vel[1] = 0
                self.pos[1] = block[1] - self.size[1]  # Align top of player with top of block
                self.onGround = 1
            elif collide == "bottom":
                self.vel[1] = 0
                self.pos[1] = block[1] + block[3] + self.size[1]
            elif collide == "left":
                self.vel[0] = 0
                self.pos[0] = block[0] - self.size[0]
            elif collide == "right":
                self.vel[0] = 0
                self.pos[0] = block[0] + block[2] + self.size[0]

        # 적과 충돌 확인 및 반응
        for enemy in self.enemies:
            block = [
                enemy.pos[0] - enemy.size[0],
                enemy.pos[1] - enemy.size[1],
                enemy.size[0] * 2 + 1,
                enemy.size[1] * 2 + 1
            ]
            r = self.colide_with(block)
            if r is not None:
                if r == "top":
                    print("Attack")
                    self.enemies.remove(enemy)
                else:
                    print("Attacked")
                    # 충돌 후 밀려나는 위치 보정
                    if r == "left":
                        self.vel = numpy.array([-2, -2], dtype='float64')
                    elif r == "right":
                        self.vel = numpy.array([2, -2], dtype='float64')
                    self.isAttacked = 20  # 충돌 후 딜레이 시간 설정
        # 위치와 속도 업데이트
        self.pos += self.vel
        self.vel[1] += 0.1  # Gravity effect
        if self.vel[1] > 5:
            self.vel[1] = 5
        if self.vel[0] > 0.3:
            self.vel[0] -= self.frac
        elif self.vel[0] < -0.3:
            self.vel[0] += self.frac
        else:
            self.vel[0] = 0

        # 충돌 딜레이 감소
        self.isAttacked = max(0, self.isAttacked - 1)

        if len(self.target) == 2:
            inblock = False
            for block in self.map.blocks:
                if block[0] < self.target[0] < block[0] + block[2] and block[1] < self.target[1] < block[1] + block[3]:
                    inblock = True
                    break
            if inblock:
                self.target_vel = numpy.zeros(2)
            self.target += self.target_vel
        else:
            self.theta += 3 * self.direction
            self.theta %= 360

    def leftKey(self):
        if self.isAttacked > 0: return
        self.vel[0] = -self.speed[0]
        self.direction = -1

    def rightKey(self):
        if self.isAttacked > 0: return
        self.vel[0] = self.speed[0]
        self.direction = 1

    def jumpKey(self):
        if self.onGround:
            self.vel[1] = -self.speed[1]
            self.onGround -= 1

    def shootKey(self):  # 갈고리 발사
        if (len(self.target) == 2):
            self.target = [0]
        else:
            # 발사 방향 설정
            angle = [math.cos(math.radians(self.theta)), math.sin(math.radians(self.theta))]
            self.target = self.pos + numpy.array(angle) * 5
            self.target_vel = numpy.array(angle) * 3

    def pullKey(self):  # 갈고리 당기기
        if len(self.target) == 2 and self.target_vel[0] == 0 and self.target_vel[1] == 0:
            # self.vel을 조정
            dx = self.target[0] - self.pos[0]
            dy = self.target[1] - self.pos[1]
            d = math.sqrt(dx * dx + dy * dy)
            if d != 0:
                dx /= d
                dy /= d
                self.vel = numpy.array([dx, dy]) * 3

    def colide_with(self, block):  # block: [x, y, w, h]
        next_pos = self.pos + self.vel
        player_left, player_right = next_pos[0] - self.size[0], next_pos[0] + self.size[0]
        player_top, player_bottom = next_pos[1] - self.size[1], next_pos[1] + self.size[1]
        block_left, block_right = block[0], block[0] + block[2]
        block_top, block_bottom = block[1], block[1] + block[3]

        if player_right > block_left and player_left < block_right:
            if player_bottom > block_top and player_top < block_bottom:
                # Determine the closest side for collision resolution
                distances = {
                    "top": abs(player_bottom - block_top),
                    "bottom": abs(player_top - block_bottom),
                    "left": abs(player_right - block_left),
                    "right": abs(player_left - block_right),
                }
                # Return the direction with the smallest distance
                return min(distances, key=distances.get)
        return None


class Enemy:

    def __init__(self, map, start_pos):
        self.map = map
        self.pos = numpy.array(start_pos, dtype='float64')
        self.vel = numpy.zeros(2)
        self.size = numpy.array([5, 5])
        self.speed = (0.3, 3)
        self.frac = 0.1
        self.size = numpy.array([5, 8])

    def player_targeting(self, player):
        # 거리가 멀면 멈춤
        if numpy.linalg.norm(player.pos - self.pos) > 200:
            self.vel[0] = 0
            return
        if player.pos[0] < self.pos[0]:
            self.vel[0] = -self.speed[0]
        elif player.pos[0] > self.pos[0]:
            self.vel[0] = self.speed[0]

    def move(self):
        # 블럭 충돌
        for block in self.map.blocks:
            collide = self.colide_with(block)
            if collide == "top":
                self.vel[1] = 0
                self.pos[1] = block[1] - self.size[1]
            elif collide == "bottom":
                self.vel[1] = 0
                self.pos[1] = block[1] + block[3] + self.size[1]
            elif collide == "left":
                self.vel[0] = 0
                self.pos[0] = block[0] - self.size[0]
            elif collide == "right":
                self.vel[0] = 0
                self.pos[0] = block[0] + block[2] + self.size[0]

        self.pos += self.vel

        self.vel[1] += 0.1
        if self.vel[1] > 5:
            self.vel[1] = 5

        if self.vel[0] > 0.3:
            self.vel[0] -= self.frac
        elif self.vel[0] < -0.3:
            self.vel[0] += self.frac
        else:
            self.vel[0] = 0

    def colide_with(self, block):  # block: [x, y, w, h]
        next_pos = self.pos + self.vel
        player_left, player_right = next_pos[0] - self.size[0], next_pos[0] + self.size[0]
        player_top, player_bottom = next_pos[1] - self.size[1], next_pos[1] + self.size[1]
        block_left, block_right = block[0], block[0] + block[2]
        block_top, block_bottom = block[1], block[1] + block[3]

        if player_right > block_left and player_left < block_right:
            if player_bottom > block_top and player_top < block_bottom:
                distances = {
                    "top": abs(player_bottom - block_top),
                    "bottom": abs(player_top - block_bottom),
                    "left": abs(player_right - block_left),
                    "right": abs(player_left - block_right),
                }
                return min(distances, key=distances.get)
        return


class Map:
    def __init__(self, file_name):
        with open(file_name, 'r', encoding="utf-8") as f:
            data = json.load(f)
        self.tile_map = data["map"]
        self.size = data["size"]
        self.tileImg = {}
        for t in data["tiles"]:
            self.tileImg[int(t)] = Image.open(data["tiles"][t])
        self.tileSize = self.tileImg[1].width
        self.blocks = []
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if (self.tile_map[i][j] != 0):
                    self.blocks.append([i * self.tileSize, j * self.tileSize, self.tileSize, self.tileSize])

        self.playerStartPos = numpy.array(data["player"], dtype=numpy.float64)

        self.enemies = data["enemies"]

    def getView(self):
        view = numpy.zeros((self.size[0] * self.tileSize, self.size[1] * self.tileSize, 3), dtype=numpy.uint8)
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if (self.tile_map[i][j] != 0):
                    view[i * self.tileSize:(i + 1) * self.tileSize,
                    j * self.tileSize:(j + 1) * self.tileSize] = numpy.array(self.tileImg[self.tile_map[i][j]])

        return view


class Camera:
    def __init__(self):
        self.pos = numpy.zeros(2)
        self.size = (240, 240)

    def view(self, player, map_img):
        # 카메라 뷰 설정
        if map_img.shape[0] < self.size[0] or map_img.shape[1] < self.size[1]:
            print("map size is too small")
            return

        # 플레이어 빨간색 사각형 (x-5,y-10,x+5,y+10)
        map_img[int(player.pos[0] - player.size[0]):int(player.pos[0] + player.size[0]),
        int(player.pos[1] - player.size[1]):int(player.pos[1] + player.size[1])] = (0, 255, 0)

        # 적 그리기
        for enemy in player.enemies:
            map_img[int(enemy.pos[0] - enemy.size[0]):int(enemy.pos[0] + enemy.size[0]),
            int(enemy.pos[1] - enemy.size[1]):int(enemy.pos[1] + enemy.size[1])] = (255, 0, 0)

        # target 그리기
        if len(player.target) != 2:
            # player pos->theta 방향으로 노란 네모 그리기
            pos = player.pos
            r = math.radians(player.theta)
            dotx = pos[0] + math.cos(r) * 10
            doty = pos[1] + math.sin(r) * 10
            map_img[int(dotx) - 3:int(dotx) + 3, int(doty) - 3:int(doty) + 3] = (255, 255, 0)
            map_img[int(dotx) - 2:int(dotx) + 2, int(doty) - 2:int(doty) + 2] = (0, 0, 0)

            # player pos->하얀점 방향으로 하얀선 그리기
            dx = dotx - pos[0]
            dy = doty - pos[1]
            d = math.sqrt(dx * dx + dy * dy)
            if d != 0:
                dx /= d
                dy /= d
                for i in range(int(d)):
                    map_img[int(pos[0] + dx * i) - 1:int(pos[0] + dx * i) + 1,
                    int(pos[1] + dy * i) - 1:int(pos[1] + dy * i) + 1] = (255, 255, 255)

            # player pos->theta-1 방향으로 하얀점 그리기
            for i in range(5):
                r = math.radians(player.theta - i * 20 * player.direction)
                dotx = pos[0] + math.cos(r) * 12
                doty = pos[1] + math.sin(r) * 12
                map_img[int(dotx) - 1:int(dotx) + 1, int(doty) - 1:int(doty) + 1] = (
                255 - i * 20, 255 - i * 20, 255 - i * 20)
        else:
            pos = player.target
            map_img[int(pos[0]) - 3:int(pos[0]) + 3, int(pos[1]) - 3:int(pos[1]) + 3] = (255, 255, 0)
            map_img[int(pos[0]) - 2:int(pos[0]) + 2, int(pos[1]) - 2:int(pos[1]) + 2] = (0, 0, 0)

            # target과 player 사이 선 그리기
            dotx = player.pos[0]
            doty = player.pos[1]
            now = numpy.array([dotx, doty])
            target = player.target
            dx = target[0] - now[0]
            dy = target[1] - now[1]
            d = math.sqrt(dx * dx + dy * dy)
            if d != 0:
                dx /= d
                dy /= d
                for i in range(int(d)):
                    map_img[int(now[0] + dx * i) - 1:int(now[0] + dx * i) + 1,
                    int(now[1] + dy * i) - 1:int(now[1] + dy * i) + 1] = (200, 200, 200)

        self.pos = player.pos - numpy.array([120, 120])

        self.pos[0] = max(0, min(self.pos[0], map_img.shape[0] - self.size[0]))
        self.pos[1] = max(0, min(self.pos[1], map_img.shape[1] - self.size[1]))

        view = map_img[
               int(self.pos[0]):int(self.pos[0]) + self.size[0],
               int(self.pos[1]):int(self.pos[1]) + self.size[1]
               ]

        return view
