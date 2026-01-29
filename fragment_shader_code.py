prog = """#version 410 core
in vec3 v_color;
in vec2 v_texture;

uniform sampler2D s_texture;

out vec4 FragColor;
void main() {
    FragColor = texture(s_texture, v_texture);// vec4(v_color, 1.0);
}
"""