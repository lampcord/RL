// TestFastRollout.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include "C4.h"

extern "C" {
    __declspec (dllimport) void C4_test_min_max();
    __declspec(dllexport) void C4_finalize(unsigned int min_max_depth);
}

int main()
{
    //C4_test_min_max();
    C4_finalize(6);
}

