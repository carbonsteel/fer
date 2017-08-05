#ifndef CS_FE_PARSER_FUNCTORS_HPP
#define CS_FE_PARSER_FUNCTORS_HPP


template <class Tparser>
struct ParseString : public LValueable<ParseString<Tparser>> {
    Tparser& psr;
    using String = typename Tparser::String;
    String str;
    ParseString(Tparser& psr, const String& str) :
            LValueable<ParseString>(*this), psr{psr}, str{str} {}

    auto operator()() {
        return psr.parseString(str);
    } 
};

template <class Tparser, class Tpred>
struct ConsumeString : public LValueable<ConsumeString<Tparser, Tpred>> {
    Tparser& psr;
    size_t minimum_consumed, maximum_consumed;
    Tpred& pred;
    ConsumeString(Tparser& psr, size_t minimum_consumed,
            size_t maximum_consumed, Tpred& pred)
            : LValueable<ConsumeString>(*this), psr{psr},
                minimum_consumed{minimum_consumed},
                maximum_consumed{maximum_consumed}, pred{pred} {}

    auto operator()() {
        return psr.consumeString(minimum_consumed, maximum_consumed, pred);
    } 
};


#endif // CS_FE_PARSER_FUNCTORS_HPP