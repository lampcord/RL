// dllmain.cpp : Defines the entry point for the DLL application.
#include "pch.h"
#include "C4.h"
#include <iostream>

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}


extern "C" {
    __declspec(dllexport) float C4_rollout(unsigned long long position, unsigned long long player, unsigned long long num_rollouts)
    {
        return C4::calc_rollout(position, player, num_rollouts);
    }
    __declspec(dllexport) void C4_render(unsigned long long position)
    {
        return C4::render_binary_position(position);
    }
    __declspec(dllexport) void C4_start_new_game()
    {
        C4::start_new_game();
    }
    __declspec(dllexport) void C4_save_learn()
    {
        C4::save_learn();
    }
    __declspec(dllexport) void C4_finalize(unsigned int min_max_depth)
    {
        C4::finalize(min_max_depth);
    }
    __declspec(dllexport) void C4_test_min_max()
    {
        C4::test_min_max();
    }
    __declspec(dllexport) void C4_set_parameters(char* filename, unsigned int leafs, unsigned int rollouts, unsigned int play_mode)
    {
        C4::set_parameters(filename, leafs, rollouts, play_mode);
    }
}

