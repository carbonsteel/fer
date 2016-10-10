#ifndef CS_FE_EXT_STD_TO_STRING_HPP
#define CS_FE_EXT_STD_TO_STRING_HPP

#include <sstream>
#include <string>
#include <vector>

namespace std {

string to_string(const string &str);
string to_string(void *ptr);

template <class Tstringny>
string to_string(const Tstringny &stringny) {
    return stringny.to_string();
}

template <class Tvalue>
string to_string(const std::vector<Tvalue> &vector) {
    stringstream ss{};
    ss << "[";
    for (const auto &i : vector) {
        ss << " . " << std::to_string(i);
    }
    ss << "]";
    return ss.str();
}

}


#endif // CS_FE_EXT_STD_TO_STRING_HPP