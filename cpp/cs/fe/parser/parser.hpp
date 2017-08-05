#ifndef CS_FE_PARSER_PARSER_HPP
#define CS_FE_PARSER_PARSER_HPP

#include <fstream>
#include <sstream>
#include <string>
#include <vector>

#include <cs/fe/parser/predicate.hpp>

#include <cs/fe/ext/std/iterator.hpp>
#include <cs/fe/ext/std/to_string.hpp>

struct Void {};

template <class Tresult>
struct ParseResult {
    using ResultType = Tresult; 
    struct IsError {};
    bool is_error;
    ResultType result;
    std::vector<std::string> errors;
    ParseResult() : is_error{false}, errors{} {}
    void merge(const ParseResult &parse_result) {
        is_error = is_error || parse_result.is_error;
        result = parse_result.result;
        errors.insert(end(errors),
                begin(parse_result.errors), end(parse_result.errors));
    }

    ParseResult(ResultType result)
            : is_error{false}, result{result}, errors{} {}
    ParseResult(ResultType result, const std::string& error)
            : is_error{false}, result{result}, errors{} {
        errors.push_back(error);
    }
    template <class Terror>
    ParseResult(ResultType result, const ParseResult<Terror> &parse_result)
            : is_error{false}, result{result}, errors{parse_result.errors} {}

    ParseResult(const std::string& error, IsError)
            : is_error{true}, errors{} {
        errors.push_back(error);
    }
    template <class Terror>
    ParseResult(const std::string& error, IsError,
            ParseResult<Terror> parse_result)
            : is_error{true} {
        errors.insert(begin(errors), error);
        for (auto &e : parse_result.errors) {
            e.insert(begin(e), {'.', ' '});
        }
        errors.insert(end(errors),
                begin(parse_result.errors), end(parse_result.errors));
    }
    template <class Terror, class ... Terrors>
    ParseResult(const std::string& error, IsError e,
            ParseResult<Terror> parse_result,
            Terrors&& ... parse_results)
            : ParseResult(error, e, std::forward<Terrors>(parse_results) ...) {
        for (auto &e : parse_result.errors) {
            e.insert(begin(e), {'.', ' '});
        }
        errors.insert(end(errors),
                begin(parse_result.errors), end(parse_result.errors));
    }

    std::string to_string() const {
        if (is_error) {
            std::stringstream ss;
            ss << "fail : " << std::endl;
            for (const std::string &error : /*std::reverse*/(errors)) {
                ss << " : " << error << std::endl;
            }
            return ss.str();
        } else {
            return std::string{"ok : "} + std::to_string(result);
        }
    }
    bool operator!() const {
        return is_error;
    }
};

template <class Tchar>
class Parser_ {
public:
    struct Coord {
        size_t column, line;
        Coord() : column{}, line{} {}
        Coord(size_t column, size_t line) : column{column}, line{line} {}
        std::string to_string() const {
            return std::to_string(line) + ":" + std::to_string(column);
        } 
    };
private:
    using FileStream = std::basic_fstream<Tchar>;

    Coord current_position;
    FileStream fs;

public:
    using StringStream = std::basic_stringstream<Tchar>;
    using String = std::basic_string<Tchar>;
    Parser_(const std::string& file_name) : current_position{{}, 1}, fs{file_name} {}

    Coord at() const {
        return current_position;
    }

    auto eof() const {
        using Result = ParseResult<Void>;
        using IsError = typename Result::IsError;
        if (!fs.eof()) {
            return Result{
                    std::string{}
                    + "expected eof, there is something starting at " + current_position.to_string(),
                    IsError{}};
        }

        return Result{Void{}};
    }

    template <class Tpred>
    auto consumeString(size_t minimum_consumed, size_t maximum_consumed,
            Tpred& pred) {
        using Result = ParseResult<String>;
        using IsError = typename Result::IsError;
        Tchar chr;
        StringStream ss{};
        if (fs.eof()) {
            // unexpected eof
            return Result{
                    std::string{}
                    + "unexpected eof at " + current_position.to_string() + " : " + pred.what(),
                    IsError{}};
        }
        if (!fs) {
            // some error
            return Result{
                    std::string{}
                    + "unusable fstream at " + current_position.to_string() + " : " + pred.what(),
                    IsError{}};
        }

        bool pred_result;
        size_t consumed{};
        for (;;) {
            if (fs.eof()) {
                // unexpected eof
                return Result{
                        std::string{}
                        + "unexpected eof at " + current_position.to_string() + " : " + pred.what(),
                        IsError{}};
            }

            chr = fs.peek();
            if (!fs) {
                // read error
                return Result{
                        std::string{}
                        + "read error at " + current_position.to_string() + " : " + pred.what(),
                        IsError{}};
            }

            ++consumed;
            if ((pred_result = pred(chr)) && consumed <= maximum_consumed) {
                fs.get(); // move forward
                ss << chr;

                if (chr == '\n') {
                    ++current_position.line;
                    current_position.column = 0;
                }

                ++current_position.column;
            } else {
                break;
            }
        }

        if (!pred_result && consumed <= minimum_consumed) {
            // parse error
            return Result{
                    std::string{}
                    + "unexpected character `" + chr + "' at "
                    + current_position.to_string() + " : " + pred.what(),
                    IsError{}};
        }

        return Result{ss.str()};
    }


    template <class Tbefore, class Tafter, class Tblock>
    auto parseBlock(Tbefore& before, Tafter& after, Tblock& block) {
        using Result = ParseResult<typename decltype(block())::ResultType>;
        using IsError = typename Result::IsError;
        auto result_ingored_if_ok = before();
        if (!result_ingored_if_ok) {
            return Result{
                    std::string{__PRETTY_FUNCTION__},
                    IsError{},
                    result_ingored_if_ok};
        }

        auto result = block();
        if (!result) {
            return result;
        }

        result_ingored_if_ok = after();
        if (!result_ingored_if_ok) {
            return Result{
                    std::string{__PRETTY_FUNCTION__},
                    IsError{},
                    result_ingored_if_ok};
        }

        return result;
    }

    auto parseString(const String& str) {
        using Result = ParseResult<String>;
        using IsError = typename Result::IsError;
        if (str.empty()) {
            return Result{str};
        }

        struct ParseStr {
            Parser_& psr;
            String str;
            size_t index;
            Coord at;
            ParseStr(Parser_& psr, const String& str) :
                    psr{psr}, str{str}, index{}, at{psr.current_position} {}

            auto operator()(Tchar c) {
                return c == str[index++];
            }

            std::string what() const {
                return std::string{}
                        + "expected `" + str[std::max(size_t{}, index - 1)] + "'"
                        + (str.size() > 1 ? " from string `" + str + "'" 
                            + " starting after " + at.to_string() : "");
            }
        } parse_str{*this, str};

        auto parsed = consumeString(str.size(), str.size(), parse_str);
        if (!parsed) {
            // some error
            return parsed;
        }

        if (parsed.result != str) {
            // unexpected string
            return Result{
                    std::string{}
                    + "unexpected character at " + current_position.to_string()
                    + " : expected `" + str + "'",
                    IsError{},
                    parsed};
        }

        return parsed;
    }

    template <class Tprefix, class Tparse>
    auto parseMany(size_t minimum_parsed, size_t maximum_parsed, Tprefix &prefix, Tparse &parse) {
        using ResultType = std::vector<typename decltype(parse())::ResultType>;
        using Result = ParseResult<ResultType>;
        using IsError = typename Result::IsError;
        ResultType many{};
        many.reserve(minimum_parsed);
        Result capture{};
        for (;;) {
            auto many_size = many.size();
            auto prefixed = lookahead(prefix);
            capture.merge(Result{
                    std::string{}
                    + "many-captured prefix errors",
                    IsError{},
                    prefixed});
            if (!prefixed) {
                if (many_size >= minimum_parsed) {
                    return Result{many, capture};
                }

                return Result{
                        std::string{}
                        + "expected at least " + std::to_string(minimum_parsed)
                        + " instances, where only " + std::to_string(many_size)
                        + " found",
                        IsError{},
                        capture};
            }

            auto parsed = parse();
            capture.merge(Result{
                    std::string{}
                    + "many-captured errors",
                    IsError{},
                    parsed});
            if (!parsed) {
                return Result{
                        std::string{}
                        + "expected definition after prefix",
                        IsError{},
                        capture};
            } else {
                many.push_back(parsed.result);
            }
        }
    }

    template <class Tparse>
    auto lookahead(Tparse& parse) {
        auto hereg = fs.tellg();
        using Result = decltype(parse());
        using IsError = typename Result::IsError;
        if (!fs) {
            return Result{
                    std::string{}
                    + "lookahead init failed, read error at " + current_position.to_string(),
                    IsError{}};
        }

        auto previous_position = current_position;
        auto parsed = parse();
        if (!parsed) {
            current_position = previous_position;
            fs.seekg(hereg);
            if (!fs) {
                return Result{
                        std::string{}
                        + "lookahead parse failed, read error at " + current_position.to_string(),
                        IsError{},
                        parsed};
            }

            // return it anyway and the pos will be reset to start over
            return parsed;
        }

        return parsed;
    }

    auto ignoreBlanks() {
        consumeString(0, SIZE_MAX, IsBlank{}.lvalue());
    }
};


#endif // CS_FE_PARSER_PARSER_HPP