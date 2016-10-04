#ifndef CS_FE_SYNTAX_DOMAIN_HPP
#define CS_FE_SYNTAX_DOMAIN_HPP

#include <cs/fe/syntax/axioms.hpp>


template <class Tparser>
struct DomainDefinition {
    using IdentifierType = typename Tparser::String;

    struct VariableDefinition {
        IdentifierType identifier, domain, value;
        VariableDefinition(const IdentifierType &identifier,
                const IdentifierType &value,
                const IdentifierType &domain)
                : identifier{identifier}, domain{domain}, value{value} {}
        VariableDefinition() : VariableDefinition({}, {}, {}) {}
        typename Tparser::String to_string() const {
            typename Tparser::StringStream ss{};
            ss << "." << identifier;
            if (!value.empty()) {
                ss << "=" << value;
            }
            if (!domain.empty()) {
                ss << ":" << domain;
            }
            return ss.str(); 
        }
    };
    struct TransformDefinition {
        std::vector<VariableDefinition> variables;
        // todo expression
        typename Tparser::String to_string() const {
            typename Tparser::StringStream ss{};
            ss << ">";
            for (const auto& v : variables) {
                ss << v.to_string();
            }
            ss << "$<undefined>";

            return ss.str();
        }
    };
    DomainDefinition *domain;
    IdentifierType identifier, transform_domain;
    std::vector<VariableDefinition> variables;
    std::vector<DomainDefinition> domains;
    std::vector<TransformDefinition> transforms;
    DomainDefinition(DomainDefinition* domain)
            : domain{domain}, identifier{}, transform_domain{}, variables{},
                domains{}, transforms{} {}
    DomainDefinition() : DomainDefinition(nullptr) {}

    typename Tparser::String to_string() const {
        typename Tparser::StringStream ss{};
        ss << "|" <<  identifier;
        if (variables.empty() && domains.empty() && transforms.empty()) {
            return ss.str();
        }

        ss << "{";
        for (const auto& v : variables) {
            ss << v.to_string();
        }
        for (const auto& d : domains) {
            ss << d.to_string();
        }
        for (const auto& t : transforms) {
            ss << t.to_string();
        }
        ss << "}";

        return ss.str();
    }

    static auto prefix(Tparser &psr) {
        using Result = decltype(psr.parseString("|"));
        using IsError = typename Result::IsError;
        psr.ignoreBlanks();
        auto guard = psr.parseString("|");
        if (!guard) {
            return Result{
                    std::string{}
                    + "expected a domain definition",
                    IsError{},
                    guard};
        }

        return guard;
    }

    static auto parse(Tparser &psr, DomainDefinition *domain) {
        using DomainResultType = DomainDefinition<Tparser>;
        using DomainResult = ParseResult<DomainResultType>;
        using DomainError = typename DomainResult::IsError;
        using VariableResultType = typename DomainResultType::VariableDefinition;
        using VariableResult = ParseResult<VariableResultType>;
        using VariableError = typename VariableResult::IsError;

        DomainDefinition dd{domain};
        psr.ignoreBlanks();
        auto identifier = psr.consumeString(1, SyntaxAxioms::MAX_IDENTIFIER_LENGTH, IsAlpha{}.lvalue());
        if (!identifier) {
            return DomainResult{
                    std::string{}
                    + "expected domain identifier",
                    DomainError{},
                    identifier};
        }
        dd.identifier = identifier.result;
        
        psr.ignoreBlanks();
        auto begin_block = psr.lookahead(ParseString<Tparser>{psr, "{"}.lvalue());
        if (!begin_block) {
            return DomainResult{dd};
        }

        /* variables */
        auto variable_prefix = [&]() {
            using VariablePrefixResult = decltype(psr.parseString("|"));
            using VariablePrefixError = typename VariablePrefixResult::IsError;
            psr.ignoreBlanks();
            auto let_var = psr.parseString(".");
            if (!let_var) {
                return VariablePrefixResult{
                        std::string{}
                        + "expected start of variable definition",
                        VariablePrefixError{},
                        let_var};
            }

            return let_var;
        };
        auto variables_parse = [&]() {
            psr.ignoreBlanks();
            auto identifier_var = psr.consumeString(1, SyntaxAxioms::MAX_IDENTIFIER_LENGTH, IsAlpha{}.lvalue());
            if (!identifier_var) {
                return VariableResult{
                        std::string{}
                        + "expected variable identifier",
                        VariableError{},
                        identifier_var};
            }

            auto value_parse = [&]() {
                using IdentifierResult = ParseResult<IdentifierType>;
                using IdentifierError = typename IdentifierResult::IsError;
                psr.ignoreBlanks();
                auto begin_value = psr.parseString("=");
                if (!begin_value) {
                    return IdentifierResult{
                            std::string{}
                            + "expected variable value",
                            IdentifierError{},
                            begin_value};
                }

                psr.ignoreBlanks();
                auto value_var = psr.consumeString(1, SyntaxAxioms::MAX_IDENTIFIER_LENGTH, IsAlpha{}.lvalue());
                if (!value_var) {
                    return IdentifierResult{
                            std::string{}
                            + "expected variable value",
                            IdentifierError{},
                            value_var};
                }

                return IdentifierResult{value_var.result};
            };
            auto value_var = psr.lookahead(value_parse);

            DomainDefinition::IdentifierType domain{};
            auto domain_parse = [&]() {
                using IdentifierResult = ParseResult<IdentifierType>;
                using IdentifierError = typename IdentifierResult::IsError;
                psr.ignoreBlanks();
                auto begin_domain = psr.parseString(":");
                if (!begin_domain) {
                    return IdentifierResult{
                            std::string{}
                            + "expected variable domain",
                            IdentifierError{},
                            begin_domain};
                }

                psr.ignoreBlanks();
                auto domain_var = psr.consumeString(1, SyntaxAxioms::MAX_IDENTIFIER_LENGTH, IsAlpha{}.lvalue());
                if (!domain_var) {
                    return IdentifierResult{
                            std::string{}
                            + "expected variable domain",
                            IdentifierError{},
                            domain_var};
                }
                
                return IdentifierResult{domain_var.result};
            };
            auto domain_var = psr.lookahead(domain_parse);

            return VariableResult{
                    VariableResultType{
                            identifier_var.result,
                            value_var.result,
                            domain_var.result}};
        };
        auto variables = psr.parseMany(0, SIZE_MAX, variable_prefix, variables_parse);
        if (!variables) {
            return DomainResult{
                    std::string{}
                    + "expected variable definitions",
                    DomainError{},
                    variables};
        }
        dd.variables = variables.result;


        /* domains */
        auto domains_prefix = [&]() {
            return DomainDefinition<Tparser>::prefix(psr);
        };
        auto domains_parse = [&]() {
            return DomainDefinition<Tparser>::parse(psr, &dd);
        };
        auto domains = psr.parseMany(0, SIZE_MAX, domains_prefix, domains_parse);
        if (!domains) {
            return DomainResult{
                    std::string{}
                    + "expected domain definitions",
                    DomainError{},
                    domains};
        }
        dd.domains = domains.result;


        /* transforms */
        auto transform_prefix = [&]() {
            using Result = decltype(psr.parseString(">"));
            using IsError = typename Result::IsError;
            psr.ignoreBlanks();
            auto guard = psr.parseString(">");
            if (!guard) {
                return Result{
                        std::string{}
                        + "expected start of transform definition",
                        IsError{},
                        guard};
            }

            return guard;
        };
        auto transforms_parse = [&]() {
            using TransformResult = ParseResult<TransformDefinition>;
            using TransformError = typename TransformResult::IsError;
            auto transform_variables = psr.parseMany(0, SIZE_MAX, variable_prefix, variables_parse);
            if (!transform_variables) {
                return TransformResult{
                        std::string{}
                        + "expected transform variables",
                        TransformError{},
                        transform_variables};
            }
            TransformDefinition td{};
            td.variables = transform_variables.result;

            /* todo parse expression */
            psr.ignoreBlanks();
            auto guard = psr.parseString("$<undefined>");
            if (!guard) {
                return TransformResult{
                        std::string{}
                        + "expected transform expression",
                        TransformError{},
                        guard};
            }

            return TransformResult{td};
        };
        auto transforms = psr.parseMany(0, SIZE_MAX, transform_prefix, transforms_parse);
        if (!transforms) {
            return DomainResult{
                    std::string{}
                    + "expected transform definitions",
                    DomainError{},
                    transforms};
        }
        dd.transforms = transforms.result;


        psr.ignoreBlanks();
        auto end_block = psr.parseString("}");
        if (!end_block) {
            return DomainResult{
                    std::string{}
                    + "expected end of domain definition",
                    DomainError{},
                    variables,
                    domains,
                    transforms,
                    end_block};
        }

        return DomainResult{dd};
    }
};


#endif // CS_FE_SYNTAX_DOMAIN_HPP