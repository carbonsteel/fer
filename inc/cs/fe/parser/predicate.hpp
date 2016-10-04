#ifndef CS_FE_PARSER_PREDICATE_HPP
#define CS_FE_PARSER_PREDICATE_HPP


#include <string>

template <class T>
struct LValueable {
    T& that;
    LValueable(T& that) : that{that} {}
    T& lvalue() {
        return that;
    }
};

struct IsUnderscore : public LValueable<IsUnderscore> {
    IsUnderscore();
    bool operator()(int c);
    std::string what() const;
};
struct IsAnything : public LValueable<IsAnything> {
    IsAnything();
    bool operator()(int c);
    std::string what() const;
};
struct IsUpper: public LValueable<IsUpper> {
    IsUpper();
    bool operator()(int c);
    std::string what() const;
};
struct IsAlpha: public LValueable<IsAlpha> {
    IsAlpha();
    bool operator()(int c);
    std::string what() const;
};
struct IsSpace: public LValueable<IsSpace> {
    IsSpace();
    bool operator()(int c);
    std::string what() const;
};
struct IsLine: public LValueable<IsLine> {
    IsLine();
    bool operator()(int c);
    std::string what() const;
};
struct IsBlank: public LValueable<IsBlank> {
    IsBlank();
    bool operator()(int c);
    std::string what() const;
};


#endif // CS_FE_PARSER_PREDICATE_HPP