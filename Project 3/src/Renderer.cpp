#include "Renderer.h"
#include "CubeData.h"
#include <glad/glad.h>
#include <glm/gtc/type_ptr.hpp>
#include <fstream>
#include <sstream>
#include <iostream>

#ifdef _WIN32
#include <windows.h>
#endif
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

std::string Renderer::readFile(const char* path) {
    std::ifstream f(path);
    std::stringstream ss;
    if (!f.is_open()) {
        std::cerr << "Cannot open " << path << "\n";
        return "";
    }
    ss << f.rdbuf();
    return ss.str();
}

unsigned int Renderer::compileShader(const char* src, unsigned int type) {
    unsigned int s = glCreateShader(type);
    glShaderSource(s, 1, &src, nullptr);
    glCompileShader(s);
    int ok; glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        char log[512]; glGetShaderInfoLog(s, 512, nullptr, log);
        std::cerr << "Shader error:\n" << log << "\n";
    }
    return s;
}

unsigned int Renderer::createShaderProgram(const char* vs, const char* fs) {
    unsigned int v = compileShader(vs, GL_VERTEX_SHADER);
    unsigned int f = compileShader(fs, GL_FRAGMENT_SHADER);
    unsigned int p = glCreateProgram();
    glAttachShader(p, v); glAttachShader(p, f);
    glLinkProgram(p);
    int ok; glGetProgramiv(p, GL_LINK_STATUS, &ok);
    if (!ok) {
        char log[512]; glGetProgramInfoLog(p, 512, nullptr, log);
        std::cerr << "Program link error:\n" << log << "\n";
    }
    glDeleteShader(v); glDeleteShader(f);
    return p;
}

unsigned int Renderer::loadTexture(const std::string& path) {
    int w, h, ch;
    unsigned char* data = stbi_load(path.c_str(), &w, &h, &ch, STBI_rgb_alpha);
    if (!data) {
        std::cerr << "Failed to load " << path << "\n";
        return 0;
    }
    unsigned int tex;
    glGenTextures(1, &tex);
    glBindTexture(GL_TEXTURE_2D, tex);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data);
    glGenerateMipmap(GL_TEXTURE_2D);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    stbi_image_free(data);
    return tex;
}

Renderer::Renderer() {
    // shaders
    std::string vs = readFile("shaders/vertex_shader.glsl");
    std::string fs = readFile("shaders/fragment_shader.glsl");
    shaderProgram = createShaderProgram(vs.c_str(), fs.c_str());

    // textures
    const char* names[6] = {
      "textures/dirt.png","textures/grass.png","textures/leaves.png",
      "textures/sand.png","textures/stone.png","textures/wood.png"
    };
    for (int i = 0;i < 6;i++)
        blockTextures[i] = loadTexture(names[i]);

    // cube VAO/VBO
    glGenVertexArrays(1, &VAO);
    glGenBuffers(1, &VBO);
    glBindVertexArray(VAO);
    glBindBuffer(GL_ARRAY_BUFFER, VBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(cubeVertices), cubeVertices, GL_STATIC_DRAW);

    // pos
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
    // uv
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);

    glBindVertexArray(0);
}

Renderer::~Renderer() {
    glDeleteTextures(6, blockTextures);
    glDeleteProgram(shaderProgram);
    glDeleteBuffers(1, &VBO);
    glDeleteVertexArrays(1, &VAO);
}

void Renderer::begin(const glm::mat4& projection, const glm::mat4& viewM) {
    proj = projection;
    view = viewM;
    glUseProgram(shaderProgram);
    glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "projection"),
        1, GL_FALSE, glm::value_ptr(proj));
    glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "view"),
        1, GL_FALSE, glm::value_ptr(view));
}

void Renderer::drawCube(const glm::mat4& model, int textureIndex) {
    glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "model"),
        1, GL_FALSE, glm::value_ptr(model));
    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, blockTextures[textureIndex]);
    glUniform1i(glGetUniformLocation(shaderProgram, "blockTexture"), 0);

    glBindVertexArray(VAO);
    glDrawArrays(GL_TRIANGLES, 0, 36);
}

void Renderer::drawWireCube(const glm::mat4& model) {
    // same uniforms
    glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "model"),
        1, GL_FALSE, glm::value_ptr(model));

    // use dirt texture just to bind something
    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, blockTextures[0]);
    glUniform1i(glGetUniformLocation(shaderProgram, "blockTexture"), 0);

    // wireframe
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
    glBindVertexArray(VAO);
    glDrawArrays(GL_TRIANGLES, 0, 36);
    glBindVertexArray(0);
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
}

void Renderer::end() {
    glUseProgram(0);
}
