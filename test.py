import pygame as pg
from GameClass import *
import math
pg.init()
screen = pg.display.set_mode((240, 240))
clock = pg.time.Clock()

# player = (x,y)
camera = Camera()
map = Map("map0.json")
player = Player(map,[Enemy(map,[60,300])])
player.pos = map.playerStartPos

def step():
    global player
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_w:
                player.jumpKey()
            if event.key == pg.K_SPACE:
                player.shootKey()
        if event.type == pg.KEYUP:
            if event.key == pg.K_s:
                player.target = [0]
                player.target_vel = numpy.zeros(2)

    if pg.key.get_pressed()[pg.K_a]:
        player.leftKey()
    if pg.key.get_pressed()[pg.K_d]:
        player.rightKey()
    if pg.key.get_pressed()[pg.K_s]:
        player.pullKey()

    player.move()
    for e in player.enemies:
        e.move()
    view = camera.view(player, map.getView()) # 240*240*3
    surface = pg.surfarray.make_surface(view)

    # player pygame에 출력
    font = pg.font.SysFont("arial", 10)
    text = font.render(f'Pos: {player.pos}   Vel: {player.vel}  Theta: {player.theta}', True, (255, 255, 255))
    surface.blit(text, (0, 0))

    screen.blit(surface, (0, 0))


running = True
while running:
    step()
    step()
    step()
    step()
    step()
    step()
    step()
    step()


    # 초당 프레임 수
    pg.display.flip()
    clock.tick(15)
