from PIL import Image, ImageDraw


def makeTile(size):
    img = Image.new('RGB', (size, size), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, size-1, size-1), outline=(0, 255, 255), width=1, radius=5)

    img.save('tile.png')

makeTile(20)