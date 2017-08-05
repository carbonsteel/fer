#include <cs/fe/parser/predicate.hpp>
#include <cctype>

using namespace std;

IsUnderscore::IsUnderscore() : LValueable<IsUnderscore>(*this) {}
bool IsUnderscore::operator()(int c) {
    return c == '_';
}
string IsUnderscore::what() const {
    return "expected `_' (underscore)";
}

IsAnything::IsAnything() : LValueable<IsAnything>(*this) {}
bool IsAnything::operator()(int) {
    return true;
}
string IsAnything::what() const {
    return "expected something (anything, really, how the fuck did you get this error? -> gx@taillon.co)";
}

IsUpper::IsUpper() : LValueable<IsUpper>(*this) {}
bool IsUpper::operator()(int c) {
    return isupper(c);
}
string IsUpper::what() const {
    return "expected upper alpha (capital letter)";
}


IsAlpha::IsAlpha() : LValueable<IsAlpha>(*this) {}
bool IsAlpha::operator()(int c) {
    return isalpha(c);
}
string IsAlpha::what() const {
    return "expected alpha (letter)";
}

IsSpace::IsSpace() : LValueable<IsSpace>(*this) {}
bool IsSpace::operator()(int c) {
    return c == ' ';
}
string IsSpace::what() const {
    return "expected ` ' (space)";
}

IsLine::IsLine() : LValueable<IsLine>(*this) {}
bool IsLine::operator()(int c) {
    return c == '\n';
}
string IsLine::what() const {
    return "expected `\n' (line feed)";
}

IsBlank::IsBlank() : LValueable<IsBlank>(*this) {}
bool IsBlank::operator()(int c) {
    return c == ' ' || c == '\n';
}
string IsBlank::what() const {
    return "expected blank (space or linefeed)";
}