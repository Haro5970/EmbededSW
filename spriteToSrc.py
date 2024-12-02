from PIL import Image
import json

with open('sprites/sprite_data.json', 'r') as f:
    data = json.load(f)

sprite = Image.open('sprites/sprite.png')

for k in data.keys():
    if len(data[k])==2:
        x,y = data[k]
        x*=16
        y*=16
        img = sprite.crop((x,y,x+16,y+16))
        img.save(f'sprites/{k}.png')
    else:
        x,y,w,h = data[k]
        x*=16
        y*=16
        img = sprite.crop((x,y,x+w,y+h))
        img.save(f'src/{k}.png')