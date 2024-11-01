import numpy
from PIL import Image
import json

class Player:
    def __init__(self):
        self.pos = numpy.zeros(2)
        self.vel = numpy.zeros(2)
        self.onGround = 0
        self.speed = (1,3)
        self.size = (5,10)
        self.frac = 0.1

        self.theta = 0



    def move(self,blocks):
        for block in blocks:
            collide = self.colide_with(block)
            print(collide)
            if collide == 1:
                self.pos[0] = block[0] - self.size[0]
                self.vel[0] = 0
            elif collide == 2:
                self.pos[0] = block[0] + block[2]
                self.vel[0] = 0
            elif collide == 3:
                self.pos[1] = block[1] - self.size[1]
                self.vel[1] = 0
                self.onGround = 1
            elif collide == 4:
                self.pos[1] = block[1] + block[3]
                self.vel[1] = 0
        self.pos += self.vel

        self.vel[1] += 0.1

        if self.vel[0] > 0.3:
            self.vel[0] -= self.frac
        elif self.vel[0] < -0.3:
            self.vel[0] += self.frac
        else:
            self.vel[0] = 0

    def leftKey(self):
        self.vel[0] = -self.speed[0]

    def rightKey(self):
        self.vel[0] = self.speed[0]

    def jumpKey(self):
        if (self.onGround):
            self.vel[1] = -self.speed[1]
            self.onGround -= 1

    def rotateRight(self):
        self.theta += 30

    def rotateLeft(self):
        self.theta -= 30

    def colide_with(self, block):    # return 0,1
        next_pos = self.pos + self.vel
        data = next_pos-numpy.array(self.size).tolist(),next_pos+numpy.array(self.size).tolist()
        point = []
        for i in range(2):
            for j in range(2):
                point.append( [data[i][0],data[j][1]] )


        print(point)

        return 0



class Map:
    def __init__(self,file_name):
        with open(file_name,'r',encoding="utf-8") as f:
            data = json.load(f)
        self.tiles = data["map"]
        # 20x20
        # 0: 빈칸, 1: 벽
        self.size = data["size"]
        self.tileImg = Image.open("tile.png")
        self.tileSize = self.tileImg.width
        self.blocks = []
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if(self.tiles[i][j] == 1):
                    self.blocks.append([i*self.tileSize,j*self.tileSize,self.tileSize,self.tileSize])

        self.playerStartPos = numpy.array(data["player"],dtype=numpy.float64)
    def getView(self):
        view = numpy.zeros((self.size[0]*self.tileSize,self.size[1]*self.tileSize,3),dtype=numpy.uint8)
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if(self.tiles[i][j]):
                    view[i*self.tileSize:(i+1)*self.tileSize,j*self.tileSize:(j+1)*self.tileSize] = numpy.array(self.tileImg)
        return view


class Camera:
    def __init__(self):
        self.pos = numpy.zeros(2)
        self.size = (240, 240)

    def view(self, player, map):
        if (map.shape[0]<self.size[0] or map.shape[1]<self.size[1]):
            print("map size is too small")
            return

        self.pos = player.pos - numpy.array([120,120])

        if(self.pos[0] < 0):
            self.pos[0] = 0

        if(self.pos[1] < 0):
            self.pos[1] = 0

        if(self.pos[0] > map.shape[0]-self.size[0]):
            self.pos[0] = map.shape[0]-self.size[0]

        if(self.pos[1] > map.shape[1]-self.size[1]):
            self.pos[1] = map.shape[1]-self.size[1]

        view = map[
               int(self.pos[0]):int(self.pos[0])+self.size[0],
               int(self.pos[1]):int(self.pos[1])+self.size[1] ]
        return view