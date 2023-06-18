#ifndef CONCURRENT_QUEUE_H
#define CONCURRENT_QUEUE_H
/*
MIT License

Copyright(c) 2022 James Raynard

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files(the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and /or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions :

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include <queue>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <iostream>

// Define a namespace for the concurrent queue
namespace cq {

// Exception to throw when popping an empty queue
class concurrent_queue_exception : public std::runtime_error {
    public:
    concurrent_queue_exception() : std::runtime_error("Queue is empty") {}
    concurrent_queue_exception(const char *s) : std::runtime_error(s) {}
};

// The concurrent queue class
template <class T>
class concurrent_queue {
    // The mutex to protect the queue
    std::mutex m;
    // The wrapped queue object
    std::queue<T> q;
    // The condition variable to signal new data
    std::condition_variable cv;

    std::atomic<bool> release = false;
    std::atomic<bool> push_enabled = true;

public:
    // Use defaults for the "Rule of Five"
    concurrent_queue() = default;

    // Thread-safe call to std::queue::push()
    void push(T value) {
        std::lock_guard<std::mutex> lg(m);
        if (push_enabled)
        {
            q.push(value);
            cv.notify_one();
        }
    }

    bool pop(T& value) {
        // Lock the mutex
        std::unique_lock<std::mutex> lg(m);

        // Do not pop() an empty queue!
        cv.wait(lg, [this]() { return !q.empty() || release.load(); });
        if (release.load()) return false;

        // Save the front element's value
        value = q.front();

        // Remove the front element
        q.pop();
        return true;
    }

    void disable_push()
    {
        std::unique_lock<std::mutex> lg(m);
        push_enabled.store(false);
        while (!q.empty()) {
            q.pop();
        }
    }

    void enable_push()
    {
        std::unique_lock<std::mutex> lg(m);
        push_enabled.store(true);
    }

    size_t release_all()
    {
        release.store(true);
        cv.notify_all();
        std::unique_lock<std::mutex> lg(m);
        auto discarded_items = q.size();
        while (!q.empty()) {
            q.pop();
        }
        return discarded_items;
    }
};
} // End of namespace cq

#endif //CONCURRENT_QUEUE_H
