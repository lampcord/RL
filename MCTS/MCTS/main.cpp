#include <iostream>
#include <time.h>
#include "PerfTimer.h"
#include "Node.h"
#include <chrono>
#include <thread>

int main()
{
	PerfTimer perf_timer(true, true, true);

	auto node_container = new NodeContainerArray<unsigned int, 100, 3>();
	unsigned int position = 0;
	auto root_node = node_container->initialize(position, 0);

	perf_timer.start();
	//std::this_thread::sleep_for(1000ms);
	auto total = 0.0f;
	for (auto x = 0u; x < 1000000; x++)
	{
		for (auto y = 0u; y < 1000; y++)
		{
			total += (float)x * (float)y;
		}
	}
	cout << total << endl;
	//for (auto x = 0; x < 3; x++)
	//{
	//	position++;
	//	auto new_node = node_container->create_child_node(root_node, position, 0, x);
	//	for (auto y = 0; y < 3; y++)
	//	{
	//		position++;
	//		node_container->create_child_node(new_node, position, 0, y);
	//	}
	//}
	perf_timer.stop();
	perf_timer.print();
	node_container->dump();
}

