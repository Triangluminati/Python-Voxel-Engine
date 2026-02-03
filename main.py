from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glfw
import numpy
import pyrr
import math
import fragment_shader_code as fsc
import vertex_shader_code as vsc
import world
import textures


#press escape to focus mouse onto window
#press f1 to change between flying and walking
#wasd for movement
#mouse for direction looking
#space for jumping/flying up
#shift for flying down


def win_resize(win, width, height):
    projection = pyrr.matrix44.create_perspective_projection_matrix(80, width/height, 0.1, 100)
    #glViewport(0, 0, width, height) #already does this by default? at least on macos

if not glfw.init():
    raise Exception("couldnt initialize glfw (window)")

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)



window = glfw.create_window(1280, 720, "Voxel Engine", None, None)
glfw.set_window_size_callback(window, win_resize) #doesnt work properly for some reason
glfw.make_context_current(window)
#x y z r g b # add textures next
test_mult = 1
verts = [
         -0.5, 0.5, 0.5,     0.0, 0.0, 1.0,   0.0,   0.0, 0.0,
         -0.5, -0.5, 0.5,    1.0, 0.0, 0.0,   0.0,   0.0, 1.0,
         0.5,  0.5, 0.5,     0.0, 1.0, 0.0,   0.0,   1.0, 0.0,
         0.5, -0.5, 0.5,     1.0, 1.0, 1.0,   0.0,   1.0, 1.0,

         -0.5, 0.5, -0.5,    0.0, 0.0, 0.5,   1.0,   0.0, 0.0,
         -0.5, -0.5, -0.5,   0.0, 1.0, 0.0,   1.0,   0.0, 1.0,
         0.5,  0.5, -0.5,    0.0, 1.0, 0.0,   1.0,   1.0, 0.0,
         0.5, -0.5, -0.5,    1.0, 1.0, 1.0,   1.0,   1.0, 1.0,

         -0.5, 0.5, 0.5,     0.0, 0.0, 1.0,   2.0,   0.0, 0.0,
         0.5,  0.5, 0.5,     0.0, 1.0, 0.0,   2.0,   0.0, 1.0,
         -0.5, 0.5, -0.5,    0.0, 0.0, 0.5,   2.0,   1.0, 0.0,
         0.5,  0.5, -0.5,    0.0, 1.0, 0.0,   2.0,   1.0, 1.0,

         -0.5, -0.5, 0.5,    1.0, 0.0, 0.0,   3.0,   0.0, 0.0,
         0.5, -0.5, 0.5,     1.0, 1.0, 1.0,   3.0,   0.0, 1.0,
         -0.5, -0.5, -0.5,   0.0, 1.0, 0.0,   3.0,   1.0, 0.0,
         0.5, -0.5, -0.5,    1.0, 1.0, 1.0,   3.0,   1.0, 1.0,

         -0.5, 0.5, 0.5,     0.0, 0.0, 1.0,   4.0,   0.0, 0.0,
         -0.5, -0.5, 0.5,    1.0, 0.0, 0.0,   4.0,   0.0, 1.0,
         -0.5, 0.5, -0.5,    0.0, 0.0, 0.5,   4.0,   1.0, 0.0,
         -0.5, -0.5, -0.5,   0.0, 1.0, 0.0,   4.0,   1.0, 1.0,

         0.5,  0.5, 0.5,     0.0, 1.0, 0.0,   5.0,   0.0, 0.0,
         0.5, -0.5, 0.5,     1.0, 1.0, 1.0,   5.0,   0.0, 1.0,
         0.5,  0.5, -0.5,    0.0, 1.0, 0.0,   5.0,   1.0, 0.0,
         0.5, -0.5, -0.5,    1.0, 1.0, 1.0,   5.0,   1.0, 1.0,
         ]

verts = numpy.array(verts, dtype=numpy.float32)

inds = [0, 1, 2, 1, 2, 3,
        4, 5, 6, 5, 6, 7,
        8, 9, 10, 9, 10, 11,

        12, 13, 14, 13, 14, 15,
        16, 17, 18, 17, 18, 19,
        20, 21, 22, 21, 22, 23,
        ]

inds = numpy.array(inds, dtype=numpy.uint32)

world_data = world.World()


for x in range(-640, 640):
    for z in range(-640, 640):
        blck = world.grass_block(x, 0, z)
        #print(blck.unpack())
        world_data.add_block(blck)
#quit()
# td = [chunk.unpack() for key, chunk in world_data.chunks.items()]
# print(len(td))
# for l in td:
#     print(l[-5:])
#quit()

voxel_data = numpy.array([block.unpack() for block in world_data.get_all_blocks()], dtype=numpy.float32)

vao = glGenVertexArrays(1)
glBindVertexArray(vao)

vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, verts.itemsize * 9, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, verts.itemsize * 9, ctypes.c_void_p(12)) #36 bytes (9*4) after the verticies

glEnableVertexAttribArray(6)
glVertexAttribPointer(6, 1, GL_FLOAT, GL_FALSE, verts.itemsize * 9, ctypes.c_void_p(24))


ebo = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, inds.nbytes, inds, GL_STATIC_DRAW)

glEnableVertexAttribArray(2)
glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, verts.itemsize * 9, ctypes.c_void_p(28))

texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D_ARRAY, texture)
glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, GL_REPEAT)

glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_NEAREST)


chunk_cube_size = voxel_data.itemsize * 9 *  ( ( world.CHUNK_SIZE ** 2 ) * world.WORLD_HEIGHT )
EMPTY_CHUNK = bytes(chunk_cube_size)
instance_vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, instance_vbo)
glBufferData(GL_ARRAY_BUFFER, world_data.total_indicies * chunk_cube_size, None, GL_DYNAMIC_DRAW)


glEnableVertexAttribArray(3)
glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(0))
glVertexAttribDivisor(3, 1)

glEnableVertexAttribArray(4)
glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))
glVertexAttribDivisor(4, 1)

glEnableVertexAttribArray(5)
glVertexAttribPointer(5, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))
glVertexAttribDivisor(5, 1)

#glEnableVertexAttribArray(4)

#glEnableVertexAttribArray(4)
#glVertexAttribIPointer(4, 1, GL_INT, GL_FALSE)


#glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
#using glTexImage3D now which is a 3d texture
#like a normal texture (image) but having a depth like a 3d model
#use this to stack textures ontop of each other like a stack of papers where each paper is an image
#then the vertex buffer just chooses the right paper to pull from the stack depending on what information you give
#it (an index for the image)


#allocate space for all the textures
glTexImage3D(GL_TEXTURE_2D_ARRAY, 0, GL_RGBA8, textures.image_width, textures.image_height, len(textures.texture_list), 0, GL_RGBA, GL_UNSIGNED_BYTE, None)


#add each image to gpu memory in a 3d texture
for ind, tex in enumerate(textures.texture_data_list):
    glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0, 0, 0, ind, textures.image_width, textures.image_height, 1, GL_RGBA, GL_UNSIGNED_BYTE, tex)

shader = compileProgram(compileShader(vsc.prog, GL_VERTEX_SHADER), compileShader(fsc.prog, GL_FRAGMENT_SHADER))






glUseProgram(shader)

glClearColor(0, 0.1, 0.1, 1)

glEnable(GL_DEPTH_TEST) #so the 3d will work, basically adds z axis

glEnable(GL_BLEND) #used to display transparency in images
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) #used to display transparency in images

projection = pyrr.matrix44.create_perspective_projection_matrix(80, 1280/720, 0.1, 10000)
translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([0,0,0]))
view = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, 0]))

model_location = glGetUniformLocation(shader, "model")
projection_location = glGetUniformLocation(shader, "projection")
view_location = glGetUniformLocation(shader, "view")
voxel_position_location = glGetUniformLocation(shader, "pos")


glUniformMatrix4fv(projection_location, 1, GL_FALSE, projection)
glUniformMatrix4fv(model_location, 1, GL_FALSE, translation)
glUniformMatrix4fv(view_location, 1, GL_FALSE, view)


last_time = 0
movement_fps = 60
y_rotation = 0
x_rotation = 0
speed = 2.8 / movement_fps
max_speed = 0.05
max_jump = 0.6
xp, yp, zp = 4, -3, 4
xs, ys, zs = 0, 0, 0
force_mouse = False
fly = True

def check_collisions(_world, x, y, z, _xs, _ys, _zs):
    np = world.Vec3(x, y, z)
    block_below = False
    block_offset = 0.6 #the distance from the center of the block to check collisions for
    # for v in _world:
    #     if _xs > 0:
    #         #if moving in positive in the x direction we dont need to worry about collisions moving in the other direction
    #         #just check collisions for this direction
    #         #we do this for all other directions
            
    #         xbp = v.x-(block_offset+0.05)
    #         if (x <= xbp and x+_xs >= xbp) and (v.y == math.floor(y+block_offset)) and v.z == math.floor(z+block_offset):
    #             _xs = xbp - x
    #     elif _xs < 0:
    #         xbp = v.x+(block_offset+0.05)
    #         if (x >= xbp and x+_xs <= xbp) and (v.y == math.floor(y+block_offset)) and v.z == math.floor(z+block_offset):
    #             _xs = xbp - x
    #     if _ys > 0:
    #         ybp = (v.y-(block_offset+0.05))
    #         if (y <= ybp and y+_ys >= ybp) and (v.x == math.floor(x+block_offset)) and v.z == math.floor(z+block_offset):
    #             _ys = ybp - y
    #             block_below = True
    #     elif _ys < 0:
    #         ybp = (v.y+(block_offset+0.05))
    #         if (y >= ybp and y+_ys <= ybp) and (v.x == math.floor(x+block_offset)) and v.z == math.floor(z+block_offset):
    #             _ys = ybp - y
    #     if _zs > 0:
    #         zbp = v.z-(block_offset+0.05)
    #         if (z <= zbp and z+_zs >= zbp) and (v.x == math.floor(x+block_offset)) and v.y == math.floor(y+block_offset):
    #             _zs = zbp - z
    #     elif _zs < 0:
    #         zbp = v.z+(block_offset+0.05)
    #         if (z >= zbp and z+_zs <= zbp) and (v.x == math.floor(x+block_offset)) and v.y == math.floor(y+block_offset):
    #             _zs = zbp - z

    np.x += _xs
    np.y += _ys
    np.z += _zs
    return (np, block_below)

def sign(v):
    if v > 0:
        return 1
    if v < 0:
        return -1
    return 0

def key_callback(window, key, code, action, mods):
    global force_mouse
    global fly
    global ys
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            force_mouse = not force_mouse
            if force_mouse:
                width, height = glfw.get_window_size(window)
                glfw.set_cursor_pos(window, width/2, height/2)
        if key == glfw.KEY_F1:
            fly = not fly
        if key == glfw.KEY_SPACE:
            if not fly:
                ys-=0.2


glfw.set_key_callback(window, key_callback)

frames = 0
last_fps_time = 0

print_loop_times = False
while not glfw.window_should_close(window):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    ttime = glfw.get_time()
    current_time = glfw.get_time()
    frames+=1
    if current_time-last_fps_time > 1:
        last_fps_time = current_time
        print(frames)
        print(f"xpos {xp}", f"ypos {yp}", f"zpos {zp}")
        print(f"chunk x = {xp//world.CHUNK_SIZE}  z = {zp//world.CHUNK_SIZE}")
        frames=0
    if current_time - last_time > 1/movement_fps:

        last_time = current_time

        if force_mouse:
            width, height = glfw.get_window_size(window)
            x_mouse, y_mouse = glfw.get_cursor_pos(window)
            y_rotation += (width/2 - x_mouse) * 0.1
            x_rotation += (height/2 - y_mouse) * 0.1
            glfw.set_cursor_pos(window, width/2, height/2)


            
        rad = math.radians(y_rotation % 360)
        ux = 0
        uy = 0
        uz = 0
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            ux += math.sin(rad) * speed
            uz += math.cos(rad) * speed
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            ux -= math.sin(rad) * speed
            uz -= math.cos(rad) * speed
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            ux += math.cos(rad) * speed
            uz -= math.sin(rad) * speed
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            ux -= math.cos(rad) * speed
            uz += math.sin(rad) * speed
        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
            if fly:
                uy-=speed
        if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
            if fly:
                uy+=speed
        
        if not fly:
            uy += speed
        xs = xs + ux - (sign(xs) * min(0.01, abs(xs))) if abs(xs) <= max_speed else sign(xs) * max_speed
        if not fly:
            ys += uy - 0.01
        else:
            ys = ys +  uy - (sign(ys) * min(0.01, abs(ys))) if abs(ys) <= max_speed else sign(ys) * max_speed
        zs = zs + uz - (sign(zs) * min(0.01, abs(zs))) if abs(zs) <= max_speed else sign(zs) * max_speed
        

        if(ys > 0):
            if not fly:
                ys = min(ys, max_jump)
            else:
                ys = min(ys, max_speed)
        else:
            if not fly:
                ys = max(ys, -max_jump)
            else:
                ys = max(ys, -max_speed)
    
    
    col_check = check_collisions(world_data, xp, yp, zp, xs, ys, zs)
    collisions = col_check[0]
    if col_check[1] and ys > 0:
        ys = 0
    xp = collisions.x
    yp = collisions.y
    zp = collisions.z
    view = pyrr.matrix44.create_from_translation(pyrr.Vector3([xp, yp, zp]))
    x_rotation_matrix = pyrr.matrix44.create_from_x_rotation(math.radians(x_rotation))
    y_rotation_matrix = pyrr.matrix44.create_from_y_rotation(math.radians(y_rotation))

    #do rotation calculations on the cpu instead of the gpu
    #much cheaper to do it once on the cpu per frame then for the shader run on the gpu


    model = pyrr.matrix44.multiply(y_rotation_matrix, x_rotation_matrix)
    glUniformMatrix4fv(model_location, 1, GL_FALSE, model)
    glUniformMatrix4fv(view_location, 1, GL_FALSE, view)
    if print_loop_times:
        print(f"everything else {glfw.get_time() - ttime}")
    ttime = glfw.get_time()
    #for v in world.gen:
    #    pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([v.x, v.y, v.z]))
    #    glUniformMatrix4fv(voxel_position_location, 1, GL_FALSE, pos)
    glBindBuffer(GL_ARRAY_BUFFER, instance_vbo)
    changed_buffer_sub_data = world_data.update(xp, yp, zp)


    # indicies_to_remove = changed_buffer_sub_data["to_unload"]
    # for value in indicies_to_remove:
    #     print("removing indices: " + str(value))
    #     #glBufferSubData(GL_ARRAY_BUFFER,  chunk_cube_size * value, chunk_cube_size, EMPTY_CHUNK)
    
    indicies_to_add = changed_buffer_sub_data["to_load"]
    for key, value in indicies_to_add:
        print("adding_indices")
        print(f"key {key}", f"val {value}")
        if key in world_data.chunks:
            print("YES")
            _data_list = world_data.chunks[key].unpack()
            _data = numpy.array(_data_list , dtype=numpy.float32)
            print(_data_list[0])
            glBufferSubData(GL_ARRAY_BUFFER,  chunk_cube_size * value, _data.nbytes, _data)
        #else:
        #    _data = EMPTY_CHUNK
        #    glBufferSubData(GL_ARRAY_BUFFER,  chunk_cube_size * value, chunk_cube_size, _data)
    if print_loop_times:
        print(f"update and buffersubdata {glfw.get_time() - ttime}")
    ttime = glfw.get_time()
    glBindVertexArray(vao)
    glUseProgram(shader)
    for key, value in world_data.loaded_chunks.items():
        n = 0
        if key in world_data.chunks:
            n = world_data.chunks[key].block_count
            glBindBuffer(GL_ARRAY_BUFFER, instance_vbo)
            b = value * chunk_cube_size

            glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(b+0))
            glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(b+12))
            glVertexAttribPointer(5, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(b+24))

            glDrawElementsInstanced(GL_TRIANGLES, inds.size, GL_UNSIGNED_INT, None, n)
    # for i in range(world_data.total_indicies):
    #     n = 0
    #     #print(world_data.loaded_chunks)
    #     #print(world_data.loaded_chunks)
        
    #     for key, value in world_data.loaded_chunks.items():
    #         #print(world_data.loaded_chunks.values())
    #         if int(i) == int(value):

    #             if key in world_data.chunks:
                    
    #                 n = world_data.chunks[key].block_count
    #                 #print(key)
    #                 glBindBuffer(GL_ARRAY_BUFFER, instance_vbo)
    #                 b = i * chunk_cube_size

    #                 glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(b+0))
    #                 glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(b+12))
    #                 glVertexAttribPointer(5, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(b+24))

    #                 glDrawElementsInstanced(GL_TRIANGLES, inds.size, GL_UNSIGNED_INT, None, n)

    if print_loop_times:
        print(f"draw everything {glfw.get_time() - ttime}")

    glfw.swap_buffers(window)

glfw.terminate()


