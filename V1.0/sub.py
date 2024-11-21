from PIL import Image, ImageDraw


def makeTile(size):
    img = Image.new('RGB', (size, size), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, size-1, size-1), outline=(255, 0, 0), width=1, radius=5)

    img.save('block2.png')

img = Image.new( "RGBA", (10,10), (160,160,160))
draw = ImageDraw.Draw(img)
draw.rectangle((1,1,3,3), fill=(0,0,0,0), width=1)
draw.rectangle((3,3,4,4), fill=(0,0,0,0), width=1)
img.save("hook.png")