from PIL import Image, ImageDraw


def makeTile(size):
    img = Image.new('RGBA', (size, size), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, size-1, size-1), outline=(250,250,250), width=1, radius=5)

    img.save('door.png')

def hook():
    img = Image.new( "RGBA", (10,10), (160,160,160))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0,0,0,0), fill=(255,255,2550,0), width=1)
    draw.rectangle((5,6,9,9), fill=(255,255,2550,0), width=1)
    draw.rectangle((9,0,9,0), fill=(255,255,2550,0), width=1)
    draw.rectangle((0,8,1,9), fill=(255,255,2550,0), width=1)
    draw.rectangle((3,3,6,6), fill=(255,255,2550,0), width=1)

    img.save("hook.png")

def enemy(x,y):
    img = Image.new( "RGBA", (x,y), (255,0,0))
    img.save("enemy.png")

makeTile(20)