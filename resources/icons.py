
from PIL import Image, ImageDraw

def create_icon(size, path):
    img  = Image.new('RGBA', (size, size), (0, 120, 212, 255))
    draw = ImageDraw.Draw(img)
    margin = size // 4
    draw.rectangle([margin, margin, size-margin, size-margin], fill=(255,255,255,255))
    img.save(path)
    print('Icono creado: ' + path)

create_icon(16, 'resources/Icon16.png')
create_icon(32, 'resources/Icon32.png')
create_icon(64, 'resources/Icon64.png')
