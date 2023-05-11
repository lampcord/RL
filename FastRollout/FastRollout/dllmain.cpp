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
    __declspec(dllexport) int add(int a, int b) {
        return a + b;
    }

    __declspec(dllexport) void print_hello() {
        std::cout << "Hello from C++!" << std::endl;
    }

    __declspec(dllexport) int add_one_million()
    {
        unsigned long long total = 0u;

        for (unsigned long long x = 0u; x < 1000000u; x++)
        {
            total += x;
        }
        return total;
    }

    __declspec(dllexport) float C4_rollout(unsigned long long position, unsigned long long player, unsigned long long num_rollouts)
    {
        return C4::calc_rollout(position, player, num_rollouts);
    }

    __declspec(dllexport) void C4_render(unsigned long long position, unsigned long long player)
    {
        return C4::render_binary_position(position, player);
    }
}

