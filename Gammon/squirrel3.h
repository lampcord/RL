#pragma once
#include <iostream>
#include <cstdint>

class Squirrel3 {
public:
    Squirrel3(uint32_t seed = 1) : state(seed) {}
    void set_seed(uint32_t seed) { state = seed; }

    uint32_t operator()() {
        state *= 0x1B851B851B851B85;
        state ^= state >> 16;
        state *= 0xDA942042E4DD58B5;
        state ^= state >> 32;
        return static_cast<uint32_t>(state);
    }

private:
    uint64_t state;
};

