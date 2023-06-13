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

	ULONGLONG GetElapsedSystemTime();
	ULONGLONG GetElapsedProcessTime();
	ULONGLONG GetElapsedThreadTime();

private:
	bool use_system;
	bool use_process;
	bool use_thread;

	ULONGLONG GetSystemTime();
	ULONGLONG system_time_start = 0u;
	ULONGLONG system_time_elapsed = 0u;

	ULONGLONG GetProcessTime();
	ULONGLONG process_time_start = 0u;
	ULONGLONG process_time_elapsed = 0u;

	ULONGLONG GetThreadTime();
	ULONGLONG thread_time_start = 0u;
	ULONGLONG thread_time_elapsed = 0u;
};

