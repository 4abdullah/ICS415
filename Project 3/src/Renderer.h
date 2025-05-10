#ifndef RENDERER_H
#define RENDERER_H

#include <glm/glm.hpp>
#include <string>

class Renderer {
public:
    Renderer();
    ~Renderer();

    void begin(const glm::mat4& projection, const glm::mat4& view);
    void end();

    void drawCube(const glm::mat4& model, int textureIndex);
    // ← declare the wireframe preview function
    void drawWireCube(const glm::mat4& model);

private:
    unsigned int VAO, VBO;
    unsigned int shaderProgram;
    unsigned int blockTextures[6];
    glm::mat4 proj, view;

    unsigned int compileShader(const char* source, unsigned int type);
    unsigned int createShaderProgram(const char* vertexSource, const char* fragmentSource);
    std::string   readFile(const char* filePath);
    unsigned int loadTexture(const std::string& path);
};

#endif // RENDERER_H
