from textures import texture_map as tm

CHUNK_SIZE = 16

class Vec3:
    x, y, z = 0,0,0
    def __init__(self, _x, _y, _z):
        self.x, self.y, self.z = _x, _y, _z


class Block(Vec3):
    texture_top = tm["default.png"]
    texture_bottom = tm["default.png"]
    texture_left = tm["default.png"]
    texture_right = tm["default.png"]
    texture_front = tm["default.png"]
    texture_back = tm["default.png"]
    def __init__(self, _x, _y, _z,
                 _texture_top = "stone.png",
                 _texture_bottom = "dirt.png",
                 _texture_left = "diorite.png",
                 _texture_right = "sand.png",
                 _texture_front = "andesite.png",
                 _texture_back = "default.png",
                 
                 ):
        self.texture_top = tm[_texture_top]
        self.texture_bottom = tm[_texture_bottom]
        self.texture_left = tm[_texture_left]
        self.texture_right = tm[_texture_right]
        self.texture_front = tm[_texture_front]
        self.texture_back = tm[_texture_back]

        super().__init__(_x, _y, _z)
        
    def set_top_texture(self, _texture_top):
        self.texture_top = tm[_texture_top]
    def set_bottom_texture(self, _texture_bottom):
        self.texture_bottom = tm[_texture_bottom]
    def set_left_texture(self, _texture_left):
        self.texture_left = tm[_texture_left]
    def set_right_texture(self, _texture_right):
        self.texture_rght = tm[_texture_right]
    def set_front_texture(self, _texture_front):
        self.texture_front = tm[_texture_front]
    def set_back_texture(self, _texture_back):
        self.exture_back = tm[_texture_back]
    #unpacks data into an array that is passable into the instance_vbo buffer
    def unpack(s):
        return [s.x, s.y, s.z, s.texture_front, s.texture_left, s.texture_right, s.texture_back, s.texture_top, s.texture_bottom]
class _Chunk:
    blocks = {}
    x_position = 0
    z_position = 0
    global CHUNK_SIZE
    def __init__(self, _x_position, _z_position):
        
        self.x_position = _x_position
        self.z_position = _z_position
    #the World class will have all of the listed functions below. These functions are not meant to be used outside of the world class
    #all x y and z values used here are normalized to the chunk (x y and z will all be between 0 and CHUNK_SIZE-1)
    def add_block(self, x, y, z, block):
        key = f"{x}{y}{z}"
        if key in self.blocks:
            return False#if theres already a block there don't just replace it
        # maybe I will add this functionality later to encourage modding
        else:
            self.blocks[key] = block
        return True
    def remove_block(self, x, y, z):
        key = f"{x}{y}{z}"
        if key in self.blocks:
            del self.blocks[key]
            return True
        return False
    def move_block(self, initial_x, initial_y, initial_z, end_x, end_y, end_z):
        x, y, z, = initial_x, initial_y, initial_z
        key = f"{x}{y}{z}"
        if not key in self.blocks:
            return False#not a block to move maybe also there can be block attributes to change what it does
        #when it moves too but just a thought for now
        self.blocks[f"{end_x}{end_y}{end_z}"] = self.blocks[key]
        del self.blocks[key]
        return True
        #all this function does it combine the add_block with remove_block
        #it adds a block in the new location, and removes the one from the old location
        #I should add some check to make sure this sequence happens correctly later
        #if I forget maybe someone willhelp me remember if its a bug lol
        #this would typically not be a function that you use though as you could move a block from one
        #chunk to another, which would be done by the World class instead

        
class World:
    global CHUNK_SIZE
    chunks = {}
    
    # you set x y and z while the blocks have their individual x y and z because the block objects contain the
    # non normalized block position which is useful to not have to recompute the global block positions
    # every time I want to pass a new chunk to the gpu
    def add_block(self, block):
        x, y, z = block.x, block.y, block.z
        chunk_x, chunk_z = x//CHUNK_SIZE, z//CHUNK_SIZE
        #maybe I can move these calculations into a more global variable that is only computed 
        # when moving chunks instead of whenever I need to make changes to the world
        chunk_key = f"{chunk_x}{chunk_z}"
        if not chunk_key in self.chunks:
            self.chunks[chunk_key] = _Chunk(chunk_x, chunk_z)

        normalized_x, normalized_y, normalized_z = x % CHUNK_SIZE, y % CHUNK_SIZE, z % CHUNK_SIZE
        
        chunk = self.chunks[chunk_key]

        valid = chunk.add_block(normalized_x, normalized_y, normalized_z, block)

        return valid
        #just tells weather or not the block was added correctly
    
    def remove_block(self, x, y, z):
        chunk_x, chunk_z = x//CHUNK_SIZE, z//CHUNK_SIZE
        chunk_key = f"{chunk_x}{chunk_z}"
        if not chunk_key in self.chunks:
            return False
            #there is no chunk so no block to remove?
        normalized_x, normalized_y, normalized_z = x % CHUNK_SIZE, y % CHUNK_SIZE, z % CHUNK_SIZE
        
        chunk = self.chunks[chunk_key]

        valid = chunk.remove_block(normalized_x, normalized_y, normalized_z)

        return valid
    
    def move_block(self, initial_x, initial_y, initial_z, end_x, end_y, end_z):
        chunk_x, chunk_z = initial_x//CHUNK_SIZE, initial_z//CHUNK_SIZE
        chunk_key = f"{chunk_x}{chunk_z}"
        if not chunk_key in self.chunks:
            return False
        normalized_x, normalized_y, normalized_z = initial_x % CHUNK_SIZE, initial_y % CHUNK_SIZE, initial_z % CHUNK_SIZE
        
        chunk = self.chunks[chunk_key]

        block_key = f"{normalized_x}{normalized_y}{normalized_z}"

        if not block_key in chunk.blocks:
            return False
        
        block = chunk.blocks[block_key]

        valid = self.add_block(end_x, end_y, end_z, block)

        if valid:
            valid = self.remove_block(initial_x, initial_y, initial_z)
        
        return valid
    def get_block(self, x, y, z):
        chunk_x, chunk_z = x//CHUNK_SIZE, z//CHUNK_SIZE
        chunk_key = f"{chunk_x}{chunk_z}"
        if not chunk_key in self.chunks:
            return None
        normalized_x, normalized_y, normalized_z = x % CHUNK_SIZE, y % CHUNK_SIZE, z % CHUNK_SIZE
        
        chunk = self.chunks[chunk_key]

        block_key = f"{normalized_x}{normalized_y}{normalized_z}"

        if not block_key in chunk.blocks:
            return None
        
        return chunk.blocks[block_key]
    def get_all_blocks(self):
        block_list = []
        for c in self.chunks.values():
            for b in c.blocks.values():
                block_list.append(b)
        return block_list





