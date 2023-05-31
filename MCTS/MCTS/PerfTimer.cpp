#include "PerfTimer.h"
#include <iostream>

using namespace std;

ULONGLONG PerfTimer::GetSystemTime()
{
	FILETIME ft;
	GetSystemTimePreciseAsFileTime(&ft);

	// Conversion of FILETIME to ULONGLONG (number of 100-nanosecond intervals since January 1, 1601 (UTC)).
	return (((ULONGLONG)ft.dwHighDateTime) << 32) + ft.dwLowDateTime;
}

ULONGLONG PerfTimer::GetProcessTime()
{
	ULONGLONG result = 0;

	FILETIME creationTime, exitTime, kernelTime, userTime;

	if (GetProcessTimes(GetCurrentProcess(), &creationTime, &exitTime, &kernelTime, &userTime))
	{
		// Conversion of FILETIME to ULONGLONG for calculations
		ULONGLONG kernelTime64 = (((ULONGLONG)kernelTime.dwHighDateTime) << 32) + kernelTime.dwLowDateTime;
		ULONGLONG userTime64 = (((ULONGLONG)userTime.dwHighDateTime) << 32) + userTime.dwLowDateTime;

		result = kernelTime64 + userTime64;
		// Now processTime contains the total CPU time of the process
	}

	return result;
}

ULONGLONG PerfTimer::GetThreadTime()
{
	ULONGLONG result = 0;

	FILETIME creationTime, exitTime, kernelTime, userTime;

	if (GetThreadTimes(GetCurrentThread(), &creationTime, &exitTime, &kernelTime, &userTime))
	{
		// Conversion of FILETIME to ULONGLONG for calculations
		ULONGLONG kernelTime64 = (((ULONGLONG)kernelTime.dwHighDateTime) << 32) + kernelTime.dwLowDateTime;
		ULONGLONG userTime64 = (((ULONGLONG)userTime.dwHighDateTime) << 32) + userTime.dwLowDateTime;

		result = kernelTime64 + userTime64;
		// Now threadTime contains the total CPU time of the thread
	}

	return result;
}

void PerfTimer::start()
{
	if (use_system)
	{
		system_time_start = GetSystemTime();
	}

	if (use_process)
	{
		process_time_start = GetProcessTime();
	}


	if (use_thread)
	{
		thread_time_start = GetThreadTime();
	}

}

void PerfTimer::stop()
{
	if (use_system)
	{
		system_time_elapsed = GetSystemTime() - system_time_start;
	}

	if (use_process)
	{
		process_time_elapsed = GetProcessTime() - process_time_start;
	}

	if (use_thread)
	{
		thread_time_elapsed = GetThreadTime() - thread_time_start;
	}
}

void PerfTimer::print()
{
	if (use_system) cout << "System: " << (float)system_time_elapsed / 10000000.0f << " ";
	if (use_process) cout << "Process: " << (float)process_time_elapsed / 10000000.0f << " ";
	if (use_thread) cout << "Thread: " << (float)thread_time_elapsed / 10000000.0f << " ";

	cout << endl;
}

