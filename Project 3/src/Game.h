#ifndef GAME_H
#define GAME_H

#include <GLFW/glfw3.h>
#include <glm/glm.hpp>
#include "Camera.h"
#include "World.h"
#include "Renderer.h"

class Game {
public:
    Game(GLFWwindow* window);
    ~Game();
    void run();

private:
    GLFWwindow* window;
    Camera      camera;
    World       world;
    Renderer    renderer;
    float       deltaTime;
    float       lastFrame;
    int         selectedType;

    void processInput();
    static void mouseButtonCallback(GLFWwindow* window, int button, int action, int mods);
    static void cursorPosCallback(GLFWwindow* window, double xpos, double ypos);

    // ← MUST declare this so the definition in Game.cpp is found
    glm::ivec3 computePlacement() const;
};

#endif // GAME_H
