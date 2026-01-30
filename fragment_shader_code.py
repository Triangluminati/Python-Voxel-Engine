prog = """#version 410 core
in vec3 v_color;
in vec2 v_texture;
in float v_texture_layer;

uniform sampler2DArray s_textures;

out vec4 FragColor;
void main() {
    FragColor = texture(s_textures, vec3(v_texture, v_texture_layer));//texture(s_texture, v_texture);// vec4(v_color, 1.0);
}
"""