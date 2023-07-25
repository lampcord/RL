#pragma once
#include "backgammon.h"
#include "console_agent.h"
#include <iostream>

float rollout(BackgammonNS::PositionStruct& position, unsigned char player, std::unique_ptr<BackgammonNS::MoveList>& move_list, unsigned int num_games, Squirrel3& rng, bool display);

//template <typename TAgentType>
//void play_games(BackgammonNS::PositionStruct& position, unsigned char player, std::unique_ptr<BackgammonNS::MoveList>& move_list, Squirrel3& rng, TAgentType& agent_0);

//void get_move(BackgammonNS::PositionStruct& position, unsigned char player, unsigned int roll, std::unique_ptr<BackgammonNS::MoveList>& move_list, Squirrel3& rng);
void print_move_set(BackgammonNS::MoveStruct& move_set, unsigned char rollout_player);

