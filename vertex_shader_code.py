prog = """#version 410 core

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_color;
layout(location = 2) in vec2 a_texture;
layout(location = 3) in vec3 i_offset;

layout(location = 4) in vec3 i_texture_flr; //front left right
layout(location = 5) in vec3 i_texture_bud; //back up down
layout(location = 6) in float face; // fb lr ud = 01 45 23

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

out vec3 v_color;
out vec2 v_texture;
out float v_texture_layer;
float get_face_layer(float face) {
    if(face == 0) return i_texture_flr.x;
    if(face == 4) return i_texture_flr.y;
    if(face == 5) return i_texture_flr.z;
    if(face == 1) return i_texture_bud.x;
    if(face == 2) return i_texture_bud.y;
    if(face == 3) return i_texture_bud.z;
}

void main() {
    vec3 world_pos = a_position + i_offset;
    gl_Position = projection * model * view * vec4(world_pos, 1.0);
    v_color = a_color;
    v_texture = a_texture;
    v_texture_layer = get_face_layer(face);
}
"""
#gl_Position = projection * model * view * vec4(a_position, 1.0);
#switch model and view to get it to be based off of offset