from PIL import Image, ImageDraw


def makeTile(size):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, size - 1, size - 1), outline=(255, 0, 0, 255), width=1, radius=5)

    img.save('block3.png')


def hook():
    img = Image.new("RGBA", (10, 10), (160, 160, 160))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 0, 0), fill=(255, 255, 2550, 0), width=1)
    draw.rectangle((5, 6, 9, 9), fill=(255, 255, 2550, 0), width=1)
    draw.rectangle((9, 0, 9, 0), fill=(255, 255, 2550, 0), width=1)
    draw.rectangle((0, 8, 1, 9), fill=(255, 255, 2550, 0), width=1)
    draw.rectangle((3, 3, 6, 6), fill=(255, 255, 2550, 0), width=1)
    draw.rectangle((1, 2, 1, 6), fill=(0, 255, 255, 255), width=1)
    draw.rectangle((2, 1, 7, 1), fill=(0, 255, 255, 255), width=1)
    draw.rectangle((8, 2, 8, 4), fill=(0, 255, 255, 255), width=1)
    draw.rectangle((3, 8, 3, 8), fill=(0, 255, 255, 255), width=1)
    draw.rectangle((2, 7, 2, 7), fill=(0, 255, 255, 255), width=1)
    img.save("hook.png")


def enemy():
    blank = (0, 0, 0, 0)
    color0 = (106, 103, 110, 255)
    colorA = (180, 180, 180, 255)
    colorB = (160, 160, 160, 255)
    img = Image.new("RGBA", (10, 18), color0)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 1, 0), fill=blank, width=1)
    draw.rectangle((0, 0, 0, 1), fill=blank, width=1)
    draw.rectangle((9, 0, 9, 0), fill=blank, width=1)
    draw.rectangle((2, 1, 8, 1), fill=colorA, width=1)
    draw.rectangle((1, 2, 8, 4), fill=colorB, width=1)
    draw.rectangle((2, 5, 8, 5), fill=colorB, width=1)
    draw.rectangle((0, 5, 0, 5), fill=blank, width=1)
    draw.rectangle((3, 3, 3, 3), fill=blank, width=1)

    img.save("enemy.png")

img = Image.open('block3.png').convert('RGBA')
draw = ImageDraw.Draw(img)
draw.line((0, 0,16,0), fill=(0, 0, 0, 0))
img.save('block3.png')