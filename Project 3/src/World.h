#ifndef WORLD_H
#define WORLD_H

#include <vector>
#include <glm/glm.hpp>
#include "Block.h"
#include "Renderer.h"

class World {
public:
    World();
    void generateTerrain();
    void render(Renderer& renderer);
    void addBlock(const glm::ivec3& pos, BlockType type);
    void removeBlock(const glm::ivec3& pos);

    // ← mark const so it can be called from computePlacement()
    bool blockExists(const glm::ivec3& pos) const;

private:
    std::vector<Block> blocks;
};

#endif // WORLD_H
