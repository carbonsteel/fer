#ifndef CS_FE_EXT_STD_TO_STRING_HPP
#define CS_FE_EXT_STD_TO_STRING_HPP

#include <string>

namespace std {

string to_string(const string& str);

template <class Tstringny>
string to_string(const Tstringny& stringny) {
    return stringny.to_string();
}

}


#endif // CS_FE_EXT_STD_TO_STRING_HPP