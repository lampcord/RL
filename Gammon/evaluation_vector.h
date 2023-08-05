#pragma once
#include <string>
#include <array>
#include <iostream>
#include <iomanip>
#include <fstream>

template <unsigned int TLength>
class EvaluationVector
{
public:
	EvaluationVector() {
		clear();
	};

	std::array<float, TLength> data;

	void dump(unsigned int digits=2);
	void clear();
	void set(float val);

	bool load(std::string filename);
	bool save(std::string filename);

	float magnitude();
	float evaluate(const EvaluationVector<TLength>&v);
	void move_towards(const EvaluationVector<TLength>& v, float target);
};


template<unsigned int TLength>
inline void EvaluationVector<TLength>::dump(unsigned int digits)
{
	using namespace std;
	
	for (auto ndx = 0u; ndx < data.size(); ndx++)
	{
		cout << fixed << setprecision(digits) << setw(digits + 4) << data[ndx] << "|";
	}
}

template<unsigned int TLength>
inline void EvaluationVector<TLength>::clear()
{
	for (auto ndx = 0u; ndx < data.size(); ndx++)
	{
		data[ndx] = 0.0f;
	}
}

template<unsigned int TLength>
inline void EvaluationVector<TLength>::set(float val)
{
	for (auto ndx = 0u; ndx < data.size(); ndx++)
	{
		data[ndx] = val;
	}
}

template<unsigned int TLength>
inline bool EvaluationVector<TLength>::load(std::string filename)
{
	std::ifstream inputFile(filename, std::ios::binary);

	if (!inputFile) {
		std::cerr << "Error opening file: " << filename << std::endl;
		return false;
	}

	inputFile.read(reinterpret_cast<char*>(data.data()), data.size() * sizeof(float));

	if (inputFile.fail()) {
		std::cerr << "Error reading file: " << filename << std::endl;
		return false;
	}

	return true;
}

template<unsigned int TLength>
inline bool EvaluationVector<TLength>::save(std::string filename)
{
	std::ofstream outputFile(filename, std::ios::binary);
	outputFile.write(reinterpret_cast<const char*>(data.data()), data.size() * sizeof(float));
	outputFile.close();
	return true;
}

template<unsigned int TLength>
inline float EvaluationVector<TLength>::magnitude()
{
	auto mag = 0.0f;

	for (auto val : data) mag += val;
	
	return mag;
}

template<unsigned int TLength>
inline float EvaluationVector<TLength>::evaluate(const EvaluationVector<TLength>& v)
{
	auto total = 0.0f;

	for (auto ndx = 0u; ndx < data.size(); ndx++)
	{
		total += data[ndx] * v.data[ndx];
	}

	return total;
}

template<unsigned int TLength>
inline void EvaluationVector<TLength>::move_towards(const EvaluationVector<TLength>& v, float target)
{
	auto actual = evaluate(v);
	auto delta = target - actual;
	auto magnitude = 0.0f;
	
	for (auto ndx = 0u; ndx < data.size(); ndx++)
	{
		//magnitude += abs(data[ndx] * v.data[ndx]);
		magnitude += abs(v.data[ndx]);
	}

	if (magnitude == 0.0f) return;

	for (auto ndx = 0u; ndx < data.size(); ndx++)
	{
		//auto val = (abs(data[ndx] * v.data[ndx]));
		auto val = (v.data[ndx]);

		auto adjustment = delta * val / magnitude;
		adjustment *= 0.001f;

		data[ndx] += adjustment;
	}

}
