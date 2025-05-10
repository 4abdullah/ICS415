// src/Game.cpp
#include "Game.h"
#include <iostream>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

static bool firstMouse = true;
static float lastX = 1280.0f / 2.0f;
static float lastY = 720.0f / 2.0f;

Game::Game(GLFWwindow* win)
    : window(win),
    // Spawn just above the center of your 70×70 world:
    camera(glm::vec3(0.0f, 20.0f, 45.0f)),
    world(),
    renderer(),
    deltaTime(0.0f),
    lastFrame(0.0f),
    selectedType(GRASS)
{
    world.generateTerrain();

    // Capture & hide the cursor
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);
    glfwSetWindowUserPointer(window, this);
    glfwSetMouseButtonCallback(window, Game::mouseButtonCallback);
    glfwSetCursorPosCallback(window, Game::cursorPosCallback);
}

Game::~Game() {}

void Game::run() {
    while (!glfwWindowShouldClose(window)) {
        float current = static_cast<float>(glfwGetTime());
        deltaTime = current - lastFrame;
        lastFrame = current;

        processInput();

        glClearColor(0.5f, 0.7f, 1.0f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        // Extend far‐plane so you can see the whole world
        glm::mat4 proj = glm::perspective(
            glm::radians(45.0f),
            1280.0f / 720.0f,
            0.1f,
            1000.0f
        );
        glm::mat4 view = camera.getViewMatrix();

        renderer.begin(proj, view);

        // 1) Draw the world
        world.render(renderer);

        // 2) Preview the placement cell in wireframe
        glm::ivec3 preview = computePlacement();
        glm::mat4 model = glm::translate(
            glm::mat4(1.0f),
            glm::vec3(preview)
        );
        renderer.drawWireCube(model);

        renderer.end();

        glfwSwapBuffers(window);
        glfwPollEvents();
    }
}

void Game::processInput() {
    if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS)   camera.processKeyboard(FORWARD, deltaTime);
    if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS)   camera.processKeyboard(BACKWARD, deltaTime);
    if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS)   camera.processKeyboard(LEFT, deltaTime);
    if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS)   camera.processKeyboard(RIGHT, deltaTime);
    if (glfwGetKey(window, GLFW_KEY_Q) == GLFW_PRESS)   camera.processKeyboard(UP, deltaTime);
    if (glfwGetKey(window, GLFW_KEY_E) == GLFW_PRESS)   camera.processKeyboard(DOWN, deltaTime);

    // 1–6 to pick block type
    for (int i = 0; i < 6; i++) {
        if (glfwGetKey(window, GLFW_KEY_1 + i) == GLFW_PRESS)
            selectedType = i;
    }
}

// Reuse your existing computePlacement() here (for the preview)...

glm::ivec3 Game::computePlacement() const {
    glm::vec3 pos = camera.getPosition();
    glm::vec3 dir = camera.getFront();
    const float step = 0.1f, maxD = 8.0f;

    glm::ivec3 lastEmpty = glm::round(pos + dir * step);
    for (float t = step; t <= maxD; t += step) {
        glm::vec3 p = pos + dir * t;
        glm::ivec3 cell = glm::round(p);
        if (world.blockExists(cell))
            return lastEmpty;
        lastEmpty = cell;
    }
    return lastEmpty;
}

// Mouse‐look callback
void Game::cursorPosCallback(GLFWwindow* window, double xpos, double ypos) {
    Game* g = static_cast<Game*>(glfwGetWindowUserPointer(window));
    if (!g) return;

    if (firstMouse) {
        lastX = (float)xpos;
        lastY = (float)ypos;
        firstMouse = false;
    }

    float xoff = (float)xpos - lastX;
    float yoff = lastY - (float)ypos;
    lastX = (float)xpos;
    lastY = (float)ypos;

    g->camera.processMouseMovement(xoff, yoff);
}

// Mouse‐click: ray‐step to find the first hit block (for removal),
// and the last empty cell before it (for addition).
void Game::mouseButtonCallback(GLFWwindow* window, int button, int action, int mods) {
    if (action != GLFW_PRESS) return;
    Game* g = static_cast<Game*>(glfwGetWindowUserPointer(window));
    if (!g) return;

    glm::vec3 pos = g->camera.getPosition();
    glm::vec3 dir = g->camera.getFront();
    const float step = 0.1f, maxD = 8.0f;

    glm::ivec3 lastEmpty = glm::round(pos + dir * step);
    bool hit = false;
    glm::ivec3 hitBlock;

    for (float t = step; t <= maxD; t += step) {
        glm::vec3 p = pos + dir * t;
        glm::ivec3 cell = glm::round(p);
        if (g->world.blockExists(cell)) {
            hit = true;
            hitBlock = cell;
            break;
        }
        lastEmpty = cell;
    }

    if (button == GLFW_MOUSE_BUTTON_LEFT && hit) {
        // Remove the block we hit
        g->world.removeBlock(hitBlock);
    }
    if (button == GLFW_MOUSE_BUTTON_RIGHT) {
        // Add at the last empty spot before the hit (or at max distance)
        glm::ivec3 place = hit ? lastEmpty : glm::round(pos + dir * maxD);
        g->world.addBlock(place, static_cast<BlockType>(g->selectedType));
    }
}
