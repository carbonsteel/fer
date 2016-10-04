#ifndef CS_FE_SYNTAX_REALM_HPP
#define CS_FE_SYNTAX_REALM_HPP

#include <string>
#include <vector>

#include <cs/fe/syntax/axioms.hpp>
#include <cs/fe/syntax/domain.hpp>

template <class Tparser>
struct RealmDefinition {
    using DomainDefinitionType = DomainDefinition<Tparser>;
    std::string identifier;
    std::vector<DomainDefinitionType> domains;

    typename Tparser::String to_string() const {
        typename Tparser::StringStream ss{};
        ss << "realm " << identifier << std::endl;
        for (const auto &d : domains) {
            ss << d.to_string() << std::endl;
        }
        return ss.str();
    }

    static auto parse(const std::string &realm_identifier) {
        Tparser psr{realm_identifier};
        using RealmResult = ParseResult<RealmDefinition>;
        using RealmError = typename RealmResult::IsError;
        RealmDefinition realm{};
        realm.identifier = realm_identifier;

        auto domains_prefix = [&]() {
            using Result = decltype(psr.parseString("domain"));
            using IsError = typename Result::IsError;
            psr.ignoreBlanks();
            auto guard = psr.parseString("domain");
            if (!guard) {
                return Result{
                        std::string{}
                        + "expected a domain of the realm",
                        IsError{},
                        guard};
            }

            return guard;
        };
        auto domains_parse = [&]() {
            return DomainDefinitionType::parse(psr, nullptr);
        };
        auto domains = psr.parseMany(1, SIZE_MAX, domains_prefix, domains_parse);
        if (!domains) {
            return RealmResult{
                    std::string{}
                    + "expected domain definitions",
                    RealmError{},
                    domains};
        }
        realm.domains = domains.result;

        auto eof = psr.eof();
        if (!eof) {
            return RealmResult{
                    std::string{}
                    + "expected end of realm definition",
                    RealmError{},
                    domains,
                    eof};
        }

        return RealmResult{realm, domains};
    }
};


#endif // CS_FE_SYNTAX_REALM_HPP