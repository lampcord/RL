#pragma once
#include <windows.h>

class PerfTimer
{
public:
	PerfTimer(bool system, bool process, bool thread)
	{
		use_system = system;
		use_process = process;
		use_thread = thread;
	}
	~PerfTimer() {};


	void start();
	void stop();
	void print();

private:
	bool use_system;
	bool use_process;
	bool use_thread;

	ULONGLONG GetSystemTime();
	ULONGLONG system_time_start;
	ULONGLONG system_time_elapsed;

	ULONGLONG GetProcessTime();
	ULONGLONG process_time_start;
	ULONGLONG process_time_elapsed;

	ULONGLONG GetThreadTime();
	ULONGLONG thread_time_start;
	ULONGLONG thread_time_elapsed;
};

