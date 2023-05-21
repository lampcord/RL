#pragma once
namespace C4
{
    void render_binary_position(unsigned long long position);
    float calc_rollout(unsigned long long position, unsigned long long player, unsigned long long num_rollouts);
    void start_new_game();
    void set_parameters(char* filename, unsigned int leafs, unsigned int rollouts, unsigned int play_mode_flag);
    void test_min_max();
    void save_learn();
    void load_learn();
    void finalize();
}