from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glfw
import numpy
import pyrr
import math
import fragment_shader_code as fsc
import vertex_shader_code as vsc
import world

def win_resize(win, width, height):
    projection = pyrr.matrix44.create_perspective_projection_matrix(80, width/height, 0.1, 100)
    #glViewport(0, 0, width, height) #already does this by default? at least on macos

if not glfw.init():
    raise Exception("couldnt initialize glfw (window)")

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)



window = glfw.create_window(1280, 720, "Title", None, None)
glfw.set_window_size_callback(window, win_resize) #doesnt work properly for some reason
glfw.make_context_current(window)
#x y z r g b # add textures next
verts = [
            
         -0.5, 0.5, 0.5, 0.0, 0.0, 1.0,
         -0.5, -0.5, 0.5, 1.0, 0.0, 0.0,
         0.5,  0.5, 0.5, 0.0, 1.0, 0.0,
         0.5, -0.5, 0.5, 1.0, 1.0, 1.0,

         -0.5, 0.5, -0.5, 0.0, 0.0, 0.5,
         -0.5, -0.5, -0.5, 0.0, 1.0, 0.0,
         0.5,  0.5, -0.5, 0.0, 1.0, 0.0,
         0.5, -0.5, -0.5, 1.0, 1.0, 1.0,
         ],
verts = numpy.array(verts, dtype=numpy.float32)

inds = [0, 1, 2, 1, 2, 3,
        4, 5, 6, 5, 6, 7,
        0, 2, 4, 2, 4, 6,
        1, 3, 5, 3, 5, 7,
        0, 1, 4, 1, 4, 5,
        2, 3, 6, 3, 6, 7
        ]

inds = numpy.array(inds, dtype=numpy.uint32)


voxel_positions = numpy.array([[v.x, v.y, v.z] for v in world.gen], dtype=numpy.float32)

vao = glGenVertexArrays(1)
glBindVertexArray(vao)

vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12)) #36 bytes (9*4) after the verticies

ebo = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, inds.nbytes, inds, GL_STATIC_DRAW)

instance_vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, instance_vbo)
glBufferData(GL_ARRAY_BUFFER, voxel_positions.nbytes, voxel_positions, GL_STATIC_DRAW)

glEnableVertexAttribArray(2)
glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
glVertexAttribDivisor(2, 1)

shader = compileProgram(compileShader(vsc.prog, GL_VERTEX_SHADER), compileShader(fsc.prog, GL_FRAGMENT_SHADER))






glUseProgram(shader)

glClearColor(0, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)

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
speed = 0.2
xp, yp, zp = 0, 0, -3
force_mouse = False



frames = 0
last_fps_time = 0
while not glfw.window_should_close(window):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    
    current_time = glfw.get_time()
    frames+=1
    if current_time-last_fps_time > 1:
        last_fps_time = current_time
        print(frames)
        frames=0
    if current_time - last_time > 1/movement_fps:

        last_time = current_time

        if force_mouse:
            width, height = glfw.get_window_size(window)
            x_mouse, y_mouse = glfw.get_cursor_pos(window)
            y_rotation += (width/2 - x_mouse) * 0.1
            x_rotation += (height/2 - y_mouse) * 0.1
            glfw.set_cursor_pos(window, width/2, height/2)


        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            force_mouse = not force_mouse
            if force_mouse:
                width, height = glfw.get_window_size(window)
                glfw.set_cursor_pos(window, width/2, height/2)
        rad = math.radians(y_rotation % 360)
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            xp += math.sin(rad) * speed
            zp += math.cos(rad) * speed
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            xp -= math.sin(rad) * speed
            zp -= math.cos(rad) * speed
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            xp += math.cos(rad) * speed
            zp -= math.sin(rad) * speed
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            xp -= math.cos(rad) * speed
            zp += math.sin(rad) * speed
        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
            yp-=speed
        if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
            yp+=speed
    view = pyrr.matrix44.create_from_translation(pyrr.Vector3([xp, yp, zp]))
    x_rotation_matrix = pyrr.matrix44.create_from_x_rotation(math.radians(x_rotation))
    y_rotation_matrix = pyrr.matrix44.create_from_y_rotation(math.radians(y_rotation))
    model = pyrr.matrix44.multiply(y_rotation_matrix, x_rotation_matrix)
    glUniformMatrix4fv(model_location, 1, GL_FALSE, model)
    glUniformMatrix4fv(view_location, 1, GL_FALSE, view)
    
    #for v in world.gen:
    #    pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([v.x, v.y, v.z]))
    #    glUniformMatrix4fv(voxel_position_location, 1, GL_FALSE, pos)
    glDrawElementsInstanced(GL_TRIANGLES, inds.size, GL_UNSIGNED_INT, None, voxel_positions.shape[0])

    glfw.swap_buffers(window)

glfw.terminate()