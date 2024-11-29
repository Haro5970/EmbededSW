import pygame as pg
from GameClass import *

pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode((240, 240))


GameStart(screen, clock)
