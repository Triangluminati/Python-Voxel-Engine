from textures import texture_map as tm
import random
import enum

CHUNK_SIZE = 16
WORLD_HEIGHT = 256
RENDER_DISTANCE = 1
#rnder_distance*render_distance chunks loaded at once
SEED = random.randint(0, 100000000) #will be useful later but I will probably use a different random method

class WORLD_TYPES(enum.Enum):
    SUPERFLAT = 0
    DEFAULT = 1 #dont use for now it wont do anything until I implement it

class Vec3:
    x, y, z = 0,0,0
    def __init__(self, _x, _y, _z):
        self.x, self.y, self.z = _x, _y, _z




class Block(Vec3):
    texture_top = None
    texture_bottom = None
    texture_left = None
    texture_right = None
    texture_front = None
    texture_back = None
    def __init__(self, _x, _y, _z,
                 _texture_top = "default.png",
                 _texture_bottom = "default.png",
                 _texture_left = "default.png",
                 _texture_right = "default.png",
                 _texture_front = "default.png",
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
        return [-s.x, s.y, -s.z, s.texture_front, s.texture_left, s.texture_right, s.texture_back, s.texture_top, s.texture_bottom]
        #for some reason I somehow flipped the x and z signs somewhere so I did this as a fix
        #if someone is reading this and knows why please send me a message or create an issue
class _Chunk:
    blocks = {}
    block_count = 0
    x_position = 0
    z_position = 0
    global CHUNK_SIZE
    def __init__(self, _x_position, _z_position):
        self.blocks = {}
        #IF YOU DONT CREATE A NEW DICTIONARY OBJECT THE BLOCKS DICTIONARY IS STORED AS A REFERENCE TO THE SAME DICTIONARY FOR ALL CHUNKS
        #I LEARNED THIS THE HARD WAY. I DEBUGGED HALF OF THE CODE BEFORE REALIZING
        self.x_position = _x_position
        self.z_position = _z_position
    #the World class will have all of the listed functions below. These functions are not meant to be used outside of the world class
    #all x y and z values used here are normalized to the chunk (x y and z will all be between 0 and CHUNK_SIZE-1)
    def add_block(self, x, y, z, block):
        key = f"{x},{y},{z}"
        if key in self.blocks:
            return False#if theres already a block there don't just replace it
        # maybe I will add this functionality later to encourage modding
        else:
            self.blocks[key] = block
        self.block_count+=1
        return True
    def remove_block(self, x, y, z):
        key = f"{x},{y},{z}"
        if key in self.blocks:
            del self.blocks[key]
            return True
        return False
    def move_block(self, initial_x, initial_y, initial_z, end_x, end_y, end_z):
        x, y, z, = initial_x, initial_y, initial_z
        key = f"{x},{y},{z}"
        if not key in self.blocks:
            return False#not a block to move maybe also there can be block attributes to change what it does
        #when it moves too but just a thought for now
        self.blocks[f"{end_x},{end_y},{end_z}"] = self.blocks[key]
        del self.blocks[key]
        return True
        #all this function does it combine the add_block with remove_block
        #it adds a block in the new location, and removes the one from the old location
        #I should add some check to make sure this sequence happens correctly later
        #if I forget maybe someone willhelp me remember if its a bug lol
        #this would typically not be a function that you use though as you could move a block from one
        #chunk to another, which would be done by the World class instead
    def unpack(self):
        return_list = []
        for key, value in self.blocks.items():
            return_list.append(value.unpack())
        return return_list

        
class World:
    global CHUNK_SIZE
    global RENDER_DISTANCE
    chunks = {}
    
    
    loaded_chunks = {}
    last_chunk_checked_at_update = None
    world_type = WORLD_TYPES.SUPERFLAT

    #precompute the offsets for the chunks in the render distance
    precomputed_distances = []
    for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
        dz_max = int((RENDER_DISTANCE ** 2 - dx*dx) ** 0.5)
        for dz in range(-dz_max, dz_max + 1):
            precomputed_distances.append((dx, dz))

    total_indicies = len(precomputed_distances)
    available_indices = [i for i in range(total_indicies)]

    # you set x y and z while the blocks have their individual x y and z because the block objects contain the
    # non normalized block position which is useful to not have to recompute the global block positions
    # every time I want to pass a new chunk to the gpu
    def add_block(self, block):
        x, y, z = block.x, block.y, block.z
        chunk_x, chunk_z = x//CHUNK_SIZE, z//CHUNK_SIZE
        #maybe I can move these calculations into a more global variable that is only computed 
        # when moving chunks instead of whenever I need to make changes to the world
        chunk_key = f"{chunk_x},{chunk_z}"
        if not chunk_key in self.chunks:
            self.chunks[chunk_key] = _Chunk(chunk_x, chunk_z)
        
        normalized_x, normalized_y, normalized_z = x % CHUNK_SIZE, y % CHUNK_SIZE, z % CHUNK_SIZE
        
        chunk = self.chunks[chunk_key]

        valid = chunk.add_block(normalized_x, normalized_y, normalized_z, block)
        #print(f"{block.unpack()} at chunk {chunk_x}, {chunk_z} | chunk key {chunk_key} | nx, ny, nz {normalized_x}, {normalized_y}, {normalized_z}")
        #print(chunk.unpack()[:3])
        return valid
        #just tells weather or not the block was added correctly
    
    def remove_block(self, x, y, z):
        chunk_x, chunk_z = x//CHUNK_SIZE, z//CHUNK_SIZE
        chunk_key = f"{chunk_x},{chunk_z}"
        if not chunk_key in self.chunks:
            return False
            #there is no chunk so no block to remove?
        normalized_x, normalized_y, normalized_z = x % CHUNK_SIZE, y % CHUNK_SIZE, z % CHUNK_SIZE
        
        chunk = self.chunks[chunk_key]

        valid = chunk.remove_block(normalized_x, normalized_y, normalized_z)

        return valid
    
    def move_block(self, initial_x, initial_y, initial_z, end_x, end_y, end_z):
        chunk_x, chunk_z = initial_x//CHUNK_SIZE, initial_z//CHUNK_SIZE
        chunk_key = f"{chunk_x},{chunk_z}"
        if not chunk_key in self.chunks:
            return False
        normalized_x, normalized_y, normalized_z = initial_x % CHUNK_SIZE, initial_y % CHUNK_SIZE, initial_z % CHUNK_SIZE
        
        chunk = self.chunks[chunk_key]

        block_key = f"{normalized_x},{normalized_y},{normalized_z}"

        if not block_key in chunk.blocks:
            return False
        
        block = chunk.blocks[block_key]

        valid = self.add_block(end_x, end_y, end_z, block)

        if valid:
            valid = self.remove_block(initial_x, initial_y, initial_z)
        
        return valid
    def get_block(self, x, y, z):
        chunk_x, chunk_z = x//CHUNK_SIZE, z//CHUNK_SIZE
        chunk_key = f"{chunk_x},{chunk_z}"
        if not chunk_key in self.chunks:
            return None
        normalized_x, normalized_y, normalized_z = x % CHUNK_SIZE, y % CHUNK_SIZE, z % CHUNK_SIZE
        
        chunk = self.chunks[chunk_key]

        block_key = f"{normalized_x},{normalized_y},{normalized_z}"

        if not block_key in chunk.blocks:
            return None
        
        return chunk.blocks[block_key]
    def get_all_blocks(self):
        block_list = []
        for c in self.chunks.values():
            for b in c.blocks.values():
                block_list.append(b)
        return block_list

    # returns a dictionary with keys "load" and "unload"
    # dictionary value for load is a list of chunk keys to load e.g. "42" for chunk 4, 2
    # I obtain the index of the offset for the buffer to load new chunks is during the unload phase, where I append the index of the chunk O unloaded into
    # a reverse sorted list in the buffer logic that has the indices that are available to load new chunks into and I just pop the indexes out as I need them
    # if there are no more available indexes just doesnt load chunks and send an error to the logs
    # the dictionary value for unload is the index of the buffer to unload
    # the pipeline for this will be unload chunks -> load new chunks
    # not sure if the I can just load the chunks over the old ones without leaving old chunk memory so I'm unloading the data just to be safe
    def update(self, player_x, player_y, player_z):
        return_dictionary = {"to_load": [], "to_unload": []}
        to_load = []
        temp_set = []
        chunk_x, chunk_z = int(player_x//CHUNK_SIZE), int(player_z//CHUNK_SIZE)
        chunk_key = f"{chunk_x},{chunk_z}"
        if not self.last_chunk_checked_at_update == None:
            if chunk_key == self.last_chunk_checked_at_update:
                return return_dictionary
        self.last_chunk_checked_at_update = chunk_key
        def func(chunk_x, chunk_z):
            current_chunk_key = f"{chunk_x},{chunk_z}"
            temp_set.append(current_chunk_key)
            if not current_chunk_key in self.loaded_chunks:
                to_load.append(current_chunk_key)
        for x_offset, z_offset in self.precomputed_distances:
            func(chunk_x + x_offset, chunk_z + z_offset)
        # for x in range(RENDER_DISTANCE):
        #     out = RENDER_DISTANCE-x
        #     func(chunk_x+x, chunk_z)
        #     if x > 0:
        #         func(chunk_x-x, chunk_z)
        #     for z in range(1, out):
        #         func(chunk_x+x, chunk_z + z)
        #         func(chunk_x+x, chunk_z - z)
        #         if x > 0:
        #             func(chunk_x-x, chunk_z + z)
        #             func(chunk_x-x, chunk_z - z)

                
        
        temp_set = set(temp_set)

        for key in set(self.loaded_chunks.keys()) - temp_set:
            self.available_indices.append(self.loaded_chunks[key])
            del self.loaded_chunks[key]
        #self.available_indices = list(sorted(self.available_indices))
        #self.available_indices.reverse()
        for c in to_load:
            new_index = self.available_indices.pop()
            self.loaded_chunks[ c ] = new_index
            return_dictionary["to_load"].append((c, new_index))
        return return_dictionary


def grass_block(x, y, z):
    return Block(x, y, z, "old_grass_top.png", "old_dirt.png", "old_grass_side.png", "old_grass_side.png", "old_grass_side.png", "old_grass_side.png")