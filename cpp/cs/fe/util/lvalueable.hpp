#ifndef CS_FE_UTIL_LVALUEABLE_HPP
#define CS_FE_UTIL_LVALUEABLE_HPP


template <class T>
struct LValueable {
    T& that;
    LValueable(T& that) : that{that} {}
    T& lvalue() {
        return that;
    }
};


#endif // CS_FE_UTIL_LVALUEABLE_HPP