import pygame as pg
from GameClass import *
import math
pg.init()
screen = pg.display.set_mode((240, 240))
clock = pg.time.Clock()

# player = (x,y)
camera = Camera()
map = Map("map0.json")
player = Player()
player.pos = map.playerStartPos

def step():
    global player
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_w:
                player.jumpKey()
            if event.key == pg.K_e:
                player.rotateRight()
            if event.key == pg.K_q:
                player.rotateLeft()
    if pg.key.get_pressed()[pg.K_a]:
        player.leftKey()
    if pg.key.get_pressed()[pg.K_d]:
        player.rightKey()

    view = map.getView()

    # 플레이어 빨간색 사각형 (x-5,y-10,x+5,y+10)
    view[int(player.pos[0]-player.size[0]):int(player.pos[0]+player.size[0]), int(player.pos[1]-player.size[1]):int(player.pos[1]+player.size[1])] = (255, 0, 0)

    # player pos->theta 방향으로 하얀점 그리기
    pos = player.pos
    r=math.radians(player.theta)
    dotx = pos[0]+math.cos(r)*10
    doty = pos[1]+math.sin(r)*10

    view[int(dotx)-1:int(dotx)+1, int(doty)-1:int(doty)+1] = (255, 255, 255)


    player.move(map.blocks)
    view = camera.view(player, view) # 240*240*3
    surface = pg.surfarray.make_surface(view)

    # player pygame에 출력
    font = pg.font.SysFont("arial", 10)
    text = font.render(f'Pos: {player.pos}   Vel: {player.vel}  Theta: {player.theta}', True, (255, 255, 255))
    surface.blit(text, (0, 0))

    screen.blit(surface, (0, 0))


running = True
while running:
    step()

    # 초당 프레임 수
    pg.display.flip()
    clock.tick(15)