#include "World.h"
#include <cmath>
#include <glm/gtc/matrix_transform.hpp>
#include <random>

World::World() {}

void World::generateTerrain() {
    int worldSize = 40;
    std::mt19937 rng(std::random_device{}());
    std::uniform_int_distribution<int> treeDist(0, 30);

    for (int x = -worldSize / 2; x < worldSize / 2; x++) {
        for (int z = -worldSize / 2; z < worldSize / 2; z++) {
            int rawH = static_cast<int>((std::sin(x * 0.5f) + std::cos(z * 0.5f)) * 2.0f);
            int h = (rawH < -1) ? -1 : rawH;

            for (int y = -1; y <= h; y++) {
                Block b;
                b.position = glm::ivec3(x, y, z);
                if (y == -1) b.type = SAND;
                else if (y == h)  b.type = GRASS;
                else              b.type = DIRT;
                blocks.push_back(b);
            }

            if (h >= 0 && treeDist(rng) == 0) {
                for (int ty = 1; ty <= 4; ty++)
                    addBlock({ x, h + ty, z }, WOOD);
                for (int dx = -2; dx <= 2; dx++)
                    for (int dy = 3; dy <= 5; dy++)
                        for (int dz = -2; dz <= 2; dz++)
                            if (std::abs(dx) + std::abs(dy - 4) + std::abs(dz) < 5)
                                addBlock({ x + dx, h + dy, z + dz }, LEAVES);
            }
        }
    }
}

void World::render(Renderer& r) {
    for (auto& b : blocks) {
        glm::mat4 model = glm::translate(glm::mat4(1.0f),
            glm::vec3(b.position));
        r.drawCube(model, static_cast<int>(b.type));
    }
}

void World::addBlock(const glm::ivec3& pos, BlockType type) {
    if (!blockExists(pos))
        blocks.push_back({ pos, type });
}

void World::removeBlock(const glm::ivec3& pos) {
    for (auto it = blocks.begin(); it != blocks.end(); ++it) {
        if (it->position == pos) {
            blocks.erase(it);
            break;
        }
    }
}

// ← signature must match header (with const at end)
bool World::blockExists(const glm::ivec3& pos) const {
    for (auto& b : blocks)
        if (b.position == pos)
            return true;
    return false;
}
