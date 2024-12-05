from typing import List
import numpy as np
import math
import json
from PIL import Image, ImageDraw, ImageOps, ImageFont
import random
import time
from colorsys import hsv_to_rgb
import board
from gpiozero import Button
from digitalio import DigitalInOut
from adafruit_rgb_display import st7789

# 디스플레이 생성
cs_pin = DigitalInOut(board.CE0)
dc_pin = DigitalInOut(board.D25)
reset_pin = DigitalInOut(board.D24)
BAUDRATE = 24000000  # SPI 통신 속도

spi = board.SPI()
disp = st7789.ST7789(
    spi,
    height=240,
    y_offset=80,
    rotation=180,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# 입력 핀:
button_A = Button(5)
button_B = Button(6)
button_L = Button(27)
button_R = Button(23)
button_U = Button(17)
button_D = Button(22)
button_C = Button(4)


class Entity:
    def __init__(self, pos, size, img_code):
        self.pos = np.array(pos, dtype="float64")  # 좌상단 꼭지점
        self.size = np.array(size, dtype="float64")
        self.vel = np.zeros(2, dtype="float64")
        self.image = img_code

    def collision(self, other, priorty=0):  # 0: no collision, 1: top, 2: bottom, 3: left, 4: right
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
                    3: abs(self_right - other_left) + priorty,  # left
                    4: abs(self_left - other_right) + priorty,  # right
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
        self.speed = 10

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
            vel = self.vel / 10
            self.vel[0] = 0
            self.vel[1] = 0
            for i in range(10):
                self.vel += vel
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

    def toPos(self, pos):
        if not self.isStuck and not self.isShooting:
            self.pos = pos - self.size / 2

    def checkCollision(self, blocks, enemies, player):
        for block in blocks:
            if block.effect == 3:
                continue
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
        super().__init__(pos, [9, 23], img_code)
        self.speed = (1, 2.2)
        self.frac = 0.1
        self.GA = 0.05

        self.heading = 1
        self.isAttacked = 0
        self.isJumping = 0

        self.hook = hook
        self.hookPullSpeed = 4

        self.door = door

        self.img = 0

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
        self.vel[0] = 1 if isleft else -1
        self.vel[1] = -1.5

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

                if block.effect == 3:
                    self.attacked(block)
        for enemy in enemies:
            collision = self.collision(enemy)
            if collision:
                if enemy.isDead:
                    # print("Player eat Enemy")
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
        self.vel[0] -= self.frac * self.heading
        if abs(self.vel[0]) < 0.2:
            self.vel[0] = 0

        # Hook Spin
        self.hook.rotate(self.heading)

        # arm pos
        armPos = self.pos + self.size / 2
        # Hook pos
        hookPos = armPos + [
            math.cos(math.radians(self.hook.angle)) * 12,
            math.sin(math.radians(self.hook.angle)) * 12
        ]
        self.hook.toPos(hookPos)


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

        self.img = 0

    def checkCollision(self, blocks):
        if self.isDead:
            return
        for block in blocks:
            if block.effect == 3:
                continue
            collision = self.collision(block, 1)
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
                if pos[0] > self.pos[0]:  # if player is right
                    self.heading = 1
                else:
                    self.heading = -1

                self.vel[0] = self.heading * self.speed[0]
        elif self.targetingFunc == 1:
            self.vel[0] = self.heading * self.speed[0]
        else:
            self.vel[0] = 0


class Map:
    def __init__(self, map_name):
        with open(map_name, "r", encoding='utf8') as f:
            map = json.load(f)

        """
        tileMap 규칙
        각 칸은 네자리수 or 0
        0: 빈칸
        천백의 자리: 사용할 타일
        십의 자리: 타일 ratate90 횟수 0~3
        일의 자리: 블럭 이펙트   0: 없음, 1: 일반 , 2: 브로큰 , 3: 공격
        """
        tileMap = map["tileMap"]
        self.mapSize = [len(tileMap[0]) * 16, len(tileMap) * 16]
        self.blockList: List["Block"] = []
        for y in range(len(tileMap)):
            for x in range(len(tileMap[y])):
                if tileMap[y][x] != 0:
                    self.blockList.append(
                        Block([x * 16, y * 16],
                              [16, 16],
                              str(tileMap[y][x] // 10),
                              tileMap[y][x] % 10))

        self.door = Door(map["doorPos"], [16, 16], "d")
        self.player = Player(
            map["playerStartPos"],
            "player",
            Hook([0, 0], "h"),
            self.door
        )
        self.player.hook.player = self.player
        self.player.move(self.blockList, [])

        self.enemyList = [Enemy(e[:2], "enemy", self.player, e[2]) for e in map["enemies"]]
        for e in self.enemyList:
            e.img += 8 * random.randint(0, 3)
        self.imageCodeTable = {}

        self.GameState = 0  # 0: 게임중, 1: 게임오버 2: 게임클리어

        self.bg = Image.open("src/map" + map_name[4:-5] + ".png").convert("RGB")

        global button_A, button_B, button_L, button_R, button_U, button_D, button_C
        button_A.when_pressed = self.player.jump
        button_B.when_pressed = self.player.shot

    def MakeImageCode(self):
        # 각 이미지 RGBA 로 로드
        with open("sprites/sprite_data.json", "r") as f:
            data = json.load(f)
        keys = sorted(data.keys())
        for i in range(len(keys)):
            if len(data[keys[i]]) == 2:
                self.imageCodeTable[str(i + 1) + '0'] = Image.open("sprites/" + keys[i] + ".png").convert("RGBA")
                self.imageCodeTable[str(i + 1) + '1'] = Image.open("sprites/" + keys[i] + ".png").convert(
                    "RGBA").rotate(90)
                self.imageCodeTable[str(i + 1) + '2'] = Image.open("sprites/" + keys[i] + ".png").convert(
                    "RGBA").rotate(180)
                self.imageCodeTable[str(i + 1) + '3'] = Image.open("sprites/" + keys[i] + ".png").convert(
                    "RGBA").rotate(270)

        self.imageCodeTable['player0'] = Image.open("src/player0.png").convert("RGBA")
        self.imageCodeTable['player1'] = Image.open("src/player1.png").convert("RGBA")
        self.imageCodeTable['player2'] = Image.open("src/player2.png").convert("RGBA")
        self.imageCodeTable['player3'] = Image.open("src/player3.png").convert("RGBA")
        self.imageCodeTable['playerD'] = Image.open("src/playerD.png").convert("RGBA")

        self.imageCodeTable['enemy0'] = Image.open("src/enemy0.png").convert("RGBA")
        self.imageCodeTable['enemy1'] = Image.open("src/enemy1.png").convert("RGBA")
        self.imageCodeTable['enemy2'] = Image.open("src/enemy2.png").convert("RGBA")
        self.imageCodeTable['enemy3'] = Image.open("src/enemy3.png").convert("RGBA")
        self.imageCodeTable['enemyD'] = Image.open("src/enemyD.png").convert("RGBA")

        self.imageCodeTable['h'] = Image.open("src/hook.png").convert("RGBA")
        self.imageCodeTable['d'] = Image.open("src/door.png").convert("RGBA")

    def getView(self):
        view = self.bg.copy()
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
        # 도착 지점
        view.paste(
            self.imageCodeTable[self.door.image],
            [int(w) for w in self.door.pos],
            self.imageCodeTable[self.door.image]
        )

        # 적
        for enemy in self.enemyList:
            # 화면에 안나오는 적 pass
            if enemy.pos[0] > cameraPos[0] + 240 or enemy.pos[0] + enemy.size[0] < cameraPos[0] or enemy.pos[1] > \
                    cameraPos[1] + 240 or enemy.pos[1] + enemy.size[1] < cameraPos[1]:
                pass
            else:
                imgCode = enemy.image + str((enemy.img // 8) % 4) if not enemy.isDead else 'enemyD'
                enemyImg = self.imageCodeTable[
                    imgCode
                ].copy()
                if enemy.heading == -1:
                    enemyImg = ImageOps.mirror(enemyImg)
                view.paste(enemyImg,
                           [int(w) for w in enemy.pos],
                           enemyImg)

        # 플레이어
        playerImg = self.imageCodeTable[
            self.player.image + str((self.player.img // 8) % 4)
            ].copy() if self.player.isAttacked == 0 else self.imageCodeTable['playerD'].copy()
        if self.player.heading == -1:
            playerImg = ImageOps.mirror(playerImg)

        view.paste(playerImg,
                   [int(w) for w in self.player.pos],
                   playerImg)

        hook = self.player.hook
        draw.line([int(w) for w in self.player.pos + self.player.size / 2] + [int(w) for w in hook.pos + hook.size / 2],
                  fill=(200, 200, 200), width=3)

        # hook 돌려서 붙이기
        hookimg = self.imageCodeTable[hook.image].rotate(-hook.angle)
        view.paste(hookimg,
                   [int(w) for w in hook.pos],
                   hookimg)

        view = view.crop((int(cameraPos[0]), int(cameraPos[1]), int(cameraPos[0] + 240), int(cameraPos[1] + 240)))
        if view.size != (240, 240):
            print("!!! ViewSize:",view.size)
        return view

    def inputKey(self):
        """
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
        """

        if button_L.is_pressed:
            self.player.goLeft()
        if button_R.is_pressed:
            self.player.goRight()
        if button_C.is_pressed:
            self.player.pull()

    def step(self):
        self.inputKey()
        self.player.move(self.blockList, self.enemyList)
        for enemy in self.enemyList:
            enemy.player_targeting()
            enemy.move(self.blockList)
        self.player.hook.move(self.blockList, self.enemyList, self.player)

        if self.player.vel[0] != 0 and not self.player.isJumping:
            self.player.img += 1
        elif self.player.isJumping:
            self.player.img = 8
        else:
            self.player.img = 0

        for enemy in self.enemyList:
            enemy.img += 1

        return self.door.isOpened

    def draw(self):
        view = self.getView()
        try:
            disp.image(view)
        except:
            print("!!!ViewSize:",view.size)


def MapPlay(map_file_name):  # Exit: 0, Restart: -1, win: ticks
    map = Map(map_file_name)
    map.MakeImageCode()

    for i in range(0, 241, 20):
        # 스크린을 위에서부터 어둡게 하기
        view = map.getView()
        draw = ImageDraw.Draw(view)
        draw.rectangle([0, i, 240, 240], fill=(0, 0, 0))
        disp.image(view)
        time.sleep(0.01)

    result = 1
    running = True
    ticks = 0
    while running:
        ticks += 1

        running = not map.step()
        map.draw()

        time.sleep(0.01)

    view = map.getView()
    draw = ImageDraw.Draw(view)
    for i in range(0, 241, 20):
        # 스크린을 위에서부터 어둡게 하기
        draw.rectangle([0, 0, 240, i], fill=(0, 0, 0))
        disp.image(view)

    if result > 0:
        return ticks
    else:
        return result


def GameStart():
    # 인트로 영상
    try:
        with open("playdata.json", "r", encoding='utf8') as f:
            playdata = json.load(f)
    except:
        playdata = {'time': -1, 'map': 0}
        IntroMP4()

    # 배경 이미지 로딩
    bgSrc = Image.open("src/homeBG.png").convert("RGB")
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 14)
    cnt = 0
    btnState = 0  # 0: play, 1: exit

    startBtn = (90, 142, 150, 162)
    exitBtn = (90, 175, 150, 195)

    def switch():
        nonlocal btnState
        btnState = 1 - btnState

    isPlaying = False
    isExit = False

    def game():
        if btnState == 1:
            nonlocal isExit
            isExit = True
        else:
            nonlocal isPlaying
            isPlaying = True

    while (not isExit):

        button_U.when_pressed = switch
        button_D.when_pressed = switch
        button_B.when_pressed = game

        if isPlaying:
            # 게임 시작
            print("Game Start")
            result = MapPlay("map/" + str(playdata['map']) + ".json")
            if result > 0:
                print("Game Clear - " + str(result))
                if playdata['time'] == -1:  # 첫 플레이
                    playdata["clear"] = 1
                    playdata["time"] = result
                    with open("playdata.json", "w", encoding='utf8') as f:
                        json.dump(playdata, f, ensure_ascii=False, indent="\t")
                else:
                    playdata["map"] = (playdata["map"] + 2) // 2 # 현재 0번과 1번 맵만 제작
                    playdata["time"] = min(playdata["time"], result)
                    with open("playdata.json", "w", encoding='utf8') as f:
                        json.dump(playdata, f, ensure_ascii=False, indent="\t")
            isPlaying = False

        # 배경 이미지 그리기
        bg = bgSrc.copy()
        draw = ImageDraw.Draw(bg)

        high_score = playdata['time']
        if high_score == -1:
            txt = "Welcome to training."
        else:
            txt = "Your record is " + str((int)(high_score / 8 * 10) / 10) + " seconds."

        txtBox = draw.textbbox((0, 0), txt, font=font)
        center = (120 - (txtBox[2] - txtBox[0]) / 2, 216)

        draw.text(center, txt, font=font, fill=(255, 255, 255))
        # 버튼 그리기
        if cnt % 5 != 0:
            if btnState == 0:
                draw.rounded_rectangle(startBtn, outline=(255, 255, 255), width=2, radius=10)
            else:
                draw.rounded_rectangle(exitBtn, outline=(255, 255, 255), width=2, radius=10)

        disp.image(bg)

        cnt += 1
        time.sleep(0.01)

    img = Image.new("RGB", (240, 240), (0, 0, 0))
    disp.image(img)


def IntroMP4():
    imageData = []
    skip = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    draw = ImageDraw.Draw(skip)
    font = ImageFont.load_default()
    draw.text((10, 220), "Press any key to skip", font=font, fill=(255, 255, 255, 255))

    # introMp4 폴더의 이미지 전부 로딩
    for i in range(0, 77):
        img = Image.open("introMp4/" + str(i) + ".png").convert("RGB")
        if i % 4 != 0:
            img.paste(
                skip,
                (0, 0),
                skip
            )
        imageData.append(img)

    # 화면 그리기
    for i in range(0, 77):
        # 만약 keyDown이 있으면 return
        if button_A.is_pressed or button_B.is_pressed or button_L.is_pressed or button_R.is_pressed or button_U.is_pressed or button_D.is_pressed or button_C.is_pressed:
            return

        # 이미지를 화면에 그리기
        img = imageData[i]
        disp.image(img)
        time.sleep(0.01)
