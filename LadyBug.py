import time
import random
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction
from gpiozero import Button
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789


class Display:

    def __init__(self):
        # 디스플레이 생성
        cs_pin = DigitalInOut(board.CE0)
        dc_pin = DigitalInOut(board.D25)
        reset_pin = DigitalInOut(board.D24)
        BAUDRATE = 24000000

        spi = board.SPI()

        self.display = st7789.ST7789(
            spi,
            height=240,
            y_offset=80,
            rotation=180,
            cs=cs_pin,
            dc=dc_pin,
            rst=reset_pin,
            baudrate=BAUDRATE,
        )

        # 백라이트 켜기
        backlight = DigitalInOut(board.D26)
        backlight.switch_to_output()
        backlight.value = True


class Entity:

    def __init__(self, pos, dir):
        self.pos = pos
        self.dir = dir
        self.img = None


class LadyBug:

    def __init__(
        self,
        display,
    ):
        self.display = display.display
        self.display_size = 240
        self.map = Image.new("RGB", (240, 240), (0, 0, 0))
        self.map_size = (150, 240)
        self.mapDraw = ImageDraw.Draw(self.map)

        self.player = Entity(
            (
                self.map_size[0] // 2,
                self.map_size[1] // 2,
            ),
            0,
        )
        self.player_size = 10

    def _drawPlayer(self):
        shape = (
            self.player.pos[0] - self.player_size,
            self.player.pos[1] - self.player_size,
            self.player.pos[0] + self.player_size,
            self.player.pos[1] + self.player_size,
        )
        self.mapDraw.ellipse(shape, fill=(255, 255, 255))

    def _drawMap(self):
        b = [
            (0, 0),
            (0, self.map_size[1] - 1),
            (self.map_size[0] - 1, self.map_size[1] - 1),
            (self.map_size[0] - 1, 0),
            (0, 0),
        ]
        for i in range(4):
            self.mapDraw.line(b[i] + b[i + 1], (255, 255, 255))

    def Draw(self):
        self._drawMap()
        self._drawPlayer()
        self.display.image(self.map)


# 입력 핀:
button_A = Button(5)
button_B = Button(6)
button_L = Button(27)
button_R = Button(23)
button_U = Button(17)
button_D = Button(22)
button_C = Button(4)

l = LadyBug(Display())
l.Draw()
