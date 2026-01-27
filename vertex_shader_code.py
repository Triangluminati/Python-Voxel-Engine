prog = """#version 410 core

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_color;
layout (location = 2) in vec3 i_offset;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

out vec3 v_color;
void main() {
    vec3 world_pos = a_position + i_offset;
    gl_Position = projection * model * view * vec4(world_pos, 1.0);
    v_color = a_color;
}
"""
#gl_Position = projection * model * view * vec4(a_position, 1.0);
#switch model and view to get it to be based off of offset