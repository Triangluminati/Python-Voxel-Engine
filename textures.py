import os
from PIL import Image
_texture_folder = "textures/"
_all_items = os.listdir(_texture_folder)

texture_list = [f for f in _all_items if os.path.isfile(os.path.join(_texture_folder, f))]
texture_data_list = [Image.open(_texture_folder + d).convert("RGBA").tobytes() for d in texture_list]
texture_map = {}
for ind, d in enumerate(texture_list):
    texture_map[d] = ind

_temp_image = Image.open(_texture_folder + texture_list[0])
image_width = _temp_image.width
image_height = _temp_image.height