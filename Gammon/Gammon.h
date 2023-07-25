#pragma once
#include "backgammon.h"

float rollout(BackgammonNS::PositionStruct& position, unsigned char player, std::unique_ptr<BackgammonNS::MoveList>& move_list, unsigned int num_games, Squirrel3& rng, bool display);
void play_against_engine(BackgammonNS::PositionStruct& position, unsigned char player, std::unique_ptr<BackgammonNS::MoveList>& move_list, Squirrel3& rng);
void print_move_set(BackgammonNS::MoveStruct& move_set, unsigned char rollout_player);
