#ifndef CS_FE_SYNTAX_DOMAIN_HPP
#define CS_FE_SYNTAX_DOMAIN_HPP

#include <memory>

#include <cs/fe/syntax/axioms.hpp>
#include <cs/fe/util/lvalueable.hpp>


template <class Tparser>
struct DomainDefinition {
    using IdentifierType = typename Tparser::String;
    using Coord = typename Tparser::Coord;
    struct VariableDefinition;

    struct VariablePrefix : public LValueable<VariablePrefix> {
        Tparser &psr;
        VariablePrefix(Tparser &psr) : LValueable<VariablePrefix>(*this), psr{psr} {}
        auto operator()() {
            using VariablePrefixResult = decltype(psr.parseString("."));
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
        }
    };
    struct TransformDefinition {
        struct ExpressionDefinition {
            struct ArgumentDefinition {
                Coord at;
                IdentifierType identifier;
                std::unique_ptr<ExpressionDefinition> value;
                ArgumentDefinition& operator=(const ArgumentDefinition &other) {
                    if (this != &other) {
                        at = other.at;
                        identifier = other.identifier;
                        if (other.value.get() != nullptr) {
                            value = std::make_unique<ExpressionDefinition>(ExpressionDefinition{*(other.value)});
                        }
                    }
                    return *this;
                }
                ArgumentDefinition() = default;
                ArgumentDefinition(const ArgumentDefinition &other)
                         : at{}, identifier{}, value{} {
                    *this = other;
                }
                std::string to_string() const {
                    typename Tparser::StringStream ss{};
                    ss << "." << identifier;
                    if (value.get() != nullptr) {
                        ss << "~";
                        ss << value->to_string();
                    }
                    return ss.str();
                }
            };

            Coord at;
            IdentifierType identifier;
            std::vector<ArgumentDefinition> arguments;
            std::unique_ptr<ExpressionDefinition> lookup;
            ExpressionDefinition& operator=(const ExpressionDefinition &other) {
                if (this != &other) {
                    at = other.at;
                    identifier = other.identifier;
                    arguments = other.arguments;
                    if (other.lookup.get() != nullptr) {
                        lookup = std::make_unique<ExpressionDefinition>(ExpressionDefinition{*(other.lookup)});
                    }
                }
                return *this;
            }
            ExpressionDefinition() = default;
            ExpressionDefinition(const ExpressionDefinition &other)
                : at{}, identifier{}, arguments{} {
                *this = other;
            }
            std::string to_string() const {
                typename Tparser::StringStream ss{};
                ss << identifier;
                if (!arguments.empty()) {
                    ss << "(";
                    for (const auto &a : arguments) {
                        ss << a.to_string();
                    }

                    ss << ")";
                }

                if (lookup != nullptr) {
                    ss << "/";
                    ss << lookup->to_string();
                }
                return ss.str();
            }
            static auto parse_lookup(Tparser &psr, ExpressionDefinition &ex) {
                using ExpressionResult = ParseResult<ExpressionDefinition>;
                using ExpressionError = typename ExpressionResult::IsError;
                
                psr.ignoreBlanks();
                auto begin_lookup = psr.lookahead(ParseString<Tparser>{psr, "/"}.lvalue());
                if (!begin_lookup) {
                    return ExpressionResult{ex};
                }

                auto expr_lookup = parse(psr);
                if (!expr_lookup) {
                    return ExpressionResult{
                            std::string{}
                            + "expected expression lookup",
                            ExpressionError{},
                            expr_lookup};
                }
                ex.lookup = std::make_unique<ExpressionDefinition>(expr_lookup.result);
                return ExpressionResult{ex};
            }
            static auto parse(Tparser &psr) {
                using ExpressionResult = ParseResult<ExpressionDefinition>;
                using ExpressionError = typename ExpressionResult::IsError;

                psr.ignoreBlanks();
                auto expression_at = psr.at();
                auto identifier = psr.consumeString(1, SyntaxAxioms::MAX_IDENTIFIER_LENGTH, IsAlpha{}.lvalue());
                if (!identifier) {
                    return ExpressionResult{
                            std::string{}
                            + "expected expression identifier",
                            ExpressionError{},
                            identifier};
                }
                ExpressionDefinition ex{};
                ex.at = expression_at;
                ex.identifier = identifier.result;

                psr.ignoreBlanks();
                auto open_args = psr.lookahead(ParseString<Tparser>{psr, "("}.lvalue());
                if (!open_args) {
                    parse_lookup(psr, ex);
                    return ExpressionResult{ex, identifier};
                }

                auto arguments_parse = [&]() {
                    using ArgumentResult = ParseResult<ArgumentDefinition>;
                    using ArgumentError = typename ArgumentResult::IsError;

                    psr.ignoreBlanks();
                    auto arg_at = psr.at();
                    auto arg_identifier = psr.consumeString(1, SyntaxAxioms::MAX_IDENTIFIER_LENGTH, IsAlpha{}.lvalue());
                    if (!arg_identifier) {
                        return ArgumentResult{
                                std::string{}
                                + "expected argument identifier",
                                ArgumentError{},
                                arg_identifier};
                    }
                    ArgumentDefinition arg{};
                    arg.at = arg_at;
                    arg.identifier = arg_identifier.result;

                    psr.ignoreBlanks();
                    auto assign = psr.parseString("~");
                    if (!assign) {
                        return ArgumentResult{
                                std::string{}
                                + "expected argument assign expression prefix",
                                ArgumentError{},
                                assign};
                    }

                    auto arg_expression = parse(psr);
                    if (!arg_expression) {
                        return ArgumentResult{
                                std::string{}
                                + "expected argument assign expression",
                                ArgumentError{},
                                arg_expression};
                    }
                    arg.value = std::make_unique<ExpressionDefinition>(arg_expression.result);

                    return ArgumentResult{arg};
                };
                auto arguments = psr.parseMany(1, SIZE_MAX, VariablePrefix{psr}.lvalue(), arguments_parse);
                if (!arguments) {
                    return ExpressionResult{
                            std::string{}
                            + "expected argument definitions",
                            ExpressionError{},
                            arguments};
                }
                ex.arguments = arguments.result;

                psr.ignoreBlanks();
                auto close_args = psr.parseString(")");
                if (!close_args) {
                    return ExpressionResult{
                            std::string{}
                            + "expected end of expression arguments",
                            ExpressionError{},
                            arguments,
                            close_args};
                }

                parse_lookup(psr, ex);
                return ExpressionResult{ex};
            }
        };

        Coord at;
        std::vector<VariableDefinition> variables;
        ExpressionDefinition expression;

        typename Tparser::String to_string() const {
            typename Tparser::StringStream ss{};
            ss << ">";
            for (const auto& v : variables) {
                ss << v.to_string();
            }
            ss << "$" << expression.to_string();

            return ss.str();
        }
    };

    struct VariableDefinition {
        Coord at;
        IdentifierType identifier;
        using ExpressionDefinition = typename TransformDefinition::ExpressionDefinition;
        ExpressionDefinition domain, value;
        VariableDefinition(const Coord &at,
                const IdentifierType &identifier,
                const ExpressionDefinition &value,
                const ExpressionDefinition &domain)
                : at{at}, identifier{identifier}, domain{domain}, value{value} {}
        VariableDefinition() : VariableDefinition({}, {}, {}, {}) {}
        typename Tparser::String to_string() const {
            typename Tparser::StringStream ss{};
            ss << "." << identifier;
            if (!value.identifier.empty()) {
                ss << "=" << value.to_string();
            }
            if (!domain.identifier.empty()) {
                ss << ":" << domain.to_string();
            }
            return ss.str(); 
        }
    };

    Coord at;
    template <class Tpointee>
    using PtrType = std::shared_ptr<Tpointee>;
    using DomainPtrType = PtrType<DomainDefinition>;
    DomainPtrType domain;
    IdentifierType identifier, transform_domain;
    std::vector<VariableDefinition> variables;
    std::vector<DomainPtrType> domains;
    std::vector<TransformDefinition> transforms;
    DomainDefinition() = default;
    DomainDefinition& operator=(const DomainDefinition &other) {
        if (this != &other) {
            at = other.at;
            identifier = other.identifier;
            variables = other.variables;
            domains = other.domains;
            transforms = other.transforms;
            domain = other.domain;
        }
        return *this;
    }
    DomainDefinition(const DomainDefinition &other)
        : at{}, domain{}, identifier{}, transform_domain{}, variables{},
                domains{}, transforms{} {
        *this = other;
    }

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
            ss << d->to_string();
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

    static auto parse(Tparser &psr, DomainPtrType domain) {
        using DomainResultInnerType = DomainDefinition<Tparser>;
        using DomainResultType = typename DomainResultInnerType::template PtrType<DomainResultInnerType>;
        using DomainResult = ParseResult<DomainResultType>;
        using DomainError = typename DomainResult::IsError;
        using VariableResultType = typename DomainResultInnerType::VariableDefinition;
        using VariableResult = ParseResult<VariableResultType>;
        using VariableError = typename VariableResult::IsError;

        auto dd = std::make_shared<DomainDefinition>(DomainDefinition{});
        dd->at = psr.at();
        dd->domain = domain;
        psr.ignoreBlanks();
        auto identifier = psr.consumeString(1, SyntaxAxioms::MAX_IDENTIFIER_LENGTH, IsAlpha{}.lvalue());
        if (!identifier) {
            return DomainResult{
                    std::string{}
                    + "expected domain identifier",
                    DomainError{},
                    identifier};
        }
        dd->identifier = identifier.result;
        
        psr.ignoreBlanks();
        auto begin_block = psr.lookahead(ParseString<Tparser>{psr, "{"}.lvalue());
        if (!begin_block) {
            return DomainResult{dd};
        }

        /* variables */
        auto variables_parse = [&]() {
            psr.ignoreBlanks();
            auto at_var = psr.at();
            auto identifier_var = psr.consumeString(1, SyntaxAxioms::MAX_IDENTIFIER_LENGTH, IsAlpha{}.lvalue());
            if (!identifier_var) {
                return VariableResult{
                        std::string{}
                        + "expected variable identifier",
                        VariableError{},
                        identifier_var};
            }

            auto value_parse = [&]() {
                using ExpressionResult = ParseResult<typename TransformDefinition::ExpressionDefinition>;
                using ExpressionError = typename ExpressionResult::IsError;
                psr.ignoreBlanks();
                auto begin_value = psr.parseString("=");
                if (!begin_value) {
                    return ExpressionResult{
                            std::string{}
                            + "expected variable value prefix",
                            ExpressionError{},
                            begin_value};
                }

                psr.ignoreBlanks();
                auto value_var = TransformDefinition::ExpressionDefinition::parse(psr);
                if (!value_var) {
                    return ExpressionResult{
                            std::string{}
                            + "expected variable value",
                            ExpressionError{},
                            value_var};
                }

                return ExpressionResult{value_var.result};
            };
            auto value_var = psr.lookahead(value_parse);

            DomainDefinition::IdentifierType domain{};
            auto domain_parse = [&]() {
                using ExpressionResult = ParseResult<typename TransformDefinition::ExpressionDefinition>;
                using ExpressionError = typename ExpressionResult::IsError;
                psr.ignoreBlanks();
                auto begin_value = psr.parseString(":");
                if (!begin_value) {
                    return ExpressionResult{
                            std::string{}
                            + "expected variable domain prefix",
                            ExpressionError{},
                            begin_value};
                }

                psr.ignoreBlanks();
                auto value_var = TransformDefinition::ExpressionDefinition::parse(psr);
                if (!value_var) {
                    return ExpressionResult{
                            std::string{}
                            + "expected variable domain",
                            ExpressionError{},
                            value_var};
                }

                return ExpressionResult{value_var.result};
            };
            auto domain_var = psr.lookahead(domain_parse);

            return VariableResult{
                    VariableResultType{
                            at_var,
                            identifier_var.result,
                            value_var.result,
                            domain_var.result}};
        };
        auto variables = psr.parseMany(0, SIZE_MAX, VariablePrefix{psr}.lvalue(), variables_parse);
        if (!variables) {
            return DomainResult{
                    std::string{}
                    + "expected variable definitions",
                    DomainError{},
                    variables};
        }
        dd->variables = variables.result;


        /* domains */
        auto domains_prefix = [&]() {
            return DomainDefinition<Tparser>::prefix(psr);
        };
        auto domains_parse = [&]() {
            return DomainDefinition<Tparser>::parse(psr, dd);
        };
        auto domains = psr.parseMany(0, SIZE_MAX, domains_prefix, domains_parse);
        if (!domains) {
            return DomainResult{
                    std::string{}
                    + "expected domain definitions",
                    DomainError{},
                    domains};
        }
        dd->domains = domains.result;


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
            auto transform_at = psr.at();
            auto transform_variables = psr.parseMany(0, SIZE_MAX, VariablePrefix{psr}.lvalue(), variables_parse);
            if (!transform_variables) {
                return TransformResult{
                        std::string{}
                        + "expected transform variables",
                        TransformError{},
                        transform_variables};
            }
            TransformDefinition td{};
            td.at = transform_at;
            td.variables = transform_variables.result;

            psr.ignoreBlanks();
            auto guard = psr.parseString("$");
            if (!guard) {
                return TransformResult{
                        std::string{}
                        + "expected transform expression",
                        TransformError{},
                        guard};
            }

            auto transform_expression = TransformDefinition::ExpressionDefinition::parse(psr);
            if (!transform_expression) {
                return TransformResult{
                        std::string{}
                        + "expected transform expression",
                        TransformError{},
                        transform_expression};
            }
            td.expression = transform_expression.result;

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
        dd->transforms = transforms.result;


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