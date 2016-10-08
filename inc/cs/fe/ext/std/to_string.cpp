#include <cs/fe/ext/std/to_string.hpp>

#include <sstream>

using namespace std;


string std::to_string(const string& str) {
    return str;
}
string std::to_string(void *ptr) {
    if (ptr == nullptr) {
        return string{"nullptr"};
    }
    stringstream ss{};
    ss << ptr;
    return ss.str();
}