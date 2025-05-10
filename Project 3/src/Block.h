#ifndef BLOCK_H
#define BLOCK_H

#include <glm/glm.hpp>

// Block types matching your textures order:
// 0=dirt,1=grass,2=leaves,3=sand,4=stone,5=wood
enum BlockType {
    DIRT = 0,
    GRASS,
    LEAVES,
    SAND,
    STONE,
    WOOD
};

struct Block {
    glm::ivec3 position;
    BlockType   type;
};

#endif // BLOCK_H
