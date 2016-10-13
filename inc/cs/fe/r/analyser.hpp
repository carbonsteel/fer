#ifndef CS_FE_R_ANALYSER_HPP
#define CS_FE_R_ANALYSER_HPP

#include <algorithm>
#include <iterator>
#include <memory>
#include <string>

#include <cs/fe/ext/std/to_string.hpp>
#include <cs/fe/syntax/realm.hpp>


/* checks for semantic integrity of a parsed realm */
template <class Tparser>
class Analyser {
    using RealmType = RealmDefinition<Tparser>;
    using DomainType = typename RealmType::DomainDefinitionType;
    using DomainPtrType = typename DomainType::DomainPtrType;
    using VariableType = typename DomainType::VariableDefinition;
    using TransformType = typename DomainType::TransformDefinition;
    using ExpressionType = typename TransformType::ExpressionDefinition;
    using ArgumentType = typename ExpressionType::ArgumentDefinition;

    struct DomainScope;
    using DomainScopePtrType = std::shared_ptr<DomainScope>;
    struct DomainScope {
        enum Scope { DOMAIN_SCOPE_LINEAR, DOMAIN_SCOPE_FULL };
        DomainScopePtrType root, parent;
        const DomainPtrType &domain;
        using VariableConstIteratorType = typename decltype(domain->variables)::const_iterator;
        const VariableConstIteratorType vbegin;
        const VariableConstIteratorType vend;
        VariableConstIteratorType vs;
        using DomainConstIteratorType = typename decltype(domain->domains)::const_iterator;
        const DomainConstIteratorType dbegin;
        const DomainConstIteratorType dend;
        DomainConstIteratorType ds;

        std::string to_string() const {
            typename Tparser::StringStream ss{};
            ss << "DomainScope {" << std::endl
               << "domain: " << domain->identifier << std::endl
               << "parent: " << parent->domain->identifier << std::endl
               << "root: " << root->domain->identifier << std::endl
               << "}" << std::endl;
            return ss.str();
        }

        DomainScope(const DomainScopePtrType &parent, const DomainPtrType &domain, Scope scope)
                : root{}, parent{parent}, domain{domain},
                  vbegin{std::cbegin(domain->variables)},
                  vend{std::cend(domain->variables)},
                  dbegin{std::cbegin(domain->domains)},
                  dend{std::cend(domain->domains)} {
            if (parent.get() != nullptr) {
                root = parent->root;
            }
            switch (scope) {
            case DOMAIN_SCOPE_LINEAR:
                vs = vbegin;
                ds = dbegin;
                break;
            case DOMAIN_SCOPE_FULL:
                vs = vend;
                ds = dend;
                break;
            }
        }
        DomainScope(const DomainScopePtrType &parent, const DomainPtrType &domain)
                : DomainScope(parent, domain, DOMAIN_SCOPE_LINEAR) {}
        DomainScope(const DomainPtrType &domain)
                : DomainScope({}, domain, DOMAIN_SCOPE_LINEAR) {}
    };
    using AnalyseResult = ParseResult<void*>;
    using AnalyseError = typename AnalyseResult::IsError;

public:
    auto analyse(const RealmType &realm) {
        auto dscope = std::make_shared<DomainScope>(DomainScope{realm.domain});
        dscope->root = dscope;
        return analyseDomain(dscope);
    }
    AnalyseResult analyseDomain(DomainScopePtrType dscope) {
        std::cout << "analyseDomain " << dscope->domain->identifier << std::endl;  
        AnalyseResult variables_check;
        for (; dscope->vs != dscope->vend; ++dscope->vs) {
            auto var_check = analyseVariable(dscope);
            variables_check.merge(var_check);
        }
        if (!variables_check) {
            return variables_check;
        }

        AnalyseResult domains_check;
        for (; dscope->ds != dscope->dend; ) {
            auto ds = dscope->ds;
            ++dscope->ds;
            auto sdscope = std::make_shared<DomainScope>(DomainScope{dscope, *ds});
            auto domain_check = analyseDomain(sdscope);
            domains_check.merge(domain_check);
        }
        if (!domains_check) {
            return domains_check;
        }

        return AnalyseResult{nullptr};
    }

    AnalyseResult analyseVariable(const DomainScopePtrType &dscope) {
        std::cout << "analyseVariable " << dscope->vs->identifier << std::endl;  
        auto same_identifier = [&](const VariableType &v) -> bool {
            return v.identifier == dscope->vs->identifier;
        };
        auto it = std::find_if(dscope->vbegin, dscope->vs, same_identifier);
        if (it != dscope->vs) {
            return AnalyseResult{
                    std::string{}
                    + "redeclaration of variable `" + dscope->vs->identifier 
                    + "' from " + it->at.to_string() + " at " + dscope->vs->at.to_string(),
                    AnalyseError{}};
        }

        auto value_ex = analyseExpression(dscope, dscope, &dscope->vs->value);
        if (!value_ex) {
            return AnalyseResult{
                    std::string{}
                    + "unexpected variable value",
                    AnalyseError{},
                    value_ex};
        }

        auto domain_ex = analyseExpression(dscope, dscope, &dscope->vs->domain);
        if (!domain_ex) {
            return AnalyseResult{
                    std::string{}
                    + "unexpected variable domain",
                    AnalyseError{},
                    domain_ex};
        }

        /* check for conflicting value and domain bounds */

        return AnalyseResult{nullptr};
    }

    AnalyseResult analyseExpression(const DomainScopePtrType &dscope,
            const DomainScopePtrType &ldscope,
            const ExpressionType * const expression_ptr) {
        if (expression_ptr == nullptr) {
            return AnalyseResult{nullptr};
        }
        const ExpressionType expression = *expression_ptr;
        if (expression.identifier.empty()) {
            /* no expression <=> nothing to do */
            return AnalyseResult{nullptr};
        }

        using VariableConstIteratorType = typename DomainScope::VariableConstIteratorType;
        using DomainConstIteratorType = typename DomainScope::DomainConstIteratorType;
        std::cout << "analyseExpression " << expression.to_string() << std::endl;
        auto var_identifier = [&](const VariableType &v) -> bool {
            return v.identifier == expression.identifier;
        };
        auto cur_scope = dscope;
        VariableConstIteratorType var;
        while (cur_scope.get() != nullptr) {
            var = std::find_if(cur_scope->vbegin, cur_scope->vs, var_identifier);
            if (var != cur_scope->vs) {
                /* expression is refering to a variable */
                break;
            } else {
                cur_scope = cur_scope->parent;
            }
        }
        /* not a defined variable */
        if (cur_scope.get() == nullptr) {
            /* look for a domain */
            auto dom_identifier = [&](const DomainPtrType &d) -> bool {
                return d->identifier == expression.identifier;
            };
            cur_scope = ldscope;
            DomainConstIteratorType dom;
            while (cur_scope.get() != nullptr) {
                dom = std::find_if(cur_scope->dbegin, cur_scope->ds, dom_identifier);
                if (dom != cur_scope->ds) {
                    /* check rest of expr */
                    break;
                } else {
                    cur_scope = cur_scope->parent;
                }
            }
            if (cur_scope.get() == nullptr) {
                std::cout << "dscope: " << dscope->to_string() << std::endl
                        << "ldscope: " << ldscope->to_string() << std::endl;
                /* can't find a corresponding identifier in the scope -> it does not exist */
                return AnalyseResult{
                        std::string{}
                        + "invalid expression identifier `"
                        + expression.identifier + "' at " + expression.at.to_string(),
                        AnalyseError{}};
            } else {
                /* found the domain */
                /* check if all its variables have arguments */
                
                auto vars = (*dom)->variables;
                std::sort(std::begin(vars), std::end(vars));
                auto itvar = std::begin(vars);
                std::cout << "analyseExpression " << expression.to_string()
                        << " domain variables " << std::to_string(vars) << std::endl;
                auto args = expression.arguments;
                std::sort(std::begin(args), std::end(args));
                auto itarg = std::begin(args);
                std::cout << "analyseExpression " << expression.to_string()
                        << " domain arguments " << std::to_string(args) << std::endl;
                
                if (vars.empty() != args.empty()) {
                    /* there's an argument where there are no variables */
                    /* or there are variables but no arguments */
                    auto verb = (vars.empty()) ? "unexpected" : "missing";

                    return AnalyseResult{
                            std::string{}
                            + verb + " argument list for domain `"
                            + (*dom)->identifier + "' in epxression at "
                            + expression.at.to_string(),
                            AnalyseError{}};
                }

                for (; itvar != std::end(vars) && itarg != std::end(args);
                        ++itvar, ++itarg) {
                    if (itvar->identifier != itarg->identifier) {
                        /* there's a variable/argument mismatch */
                        return AnalyseResult{
                                std::string{}
                                + "invalid identifier `"
                                + itarg->identifier + "' for argument at "
                                + itarg->at.to_string(),
                                AnalyseError{}};
                    }

                    auto arg_ex = analyseExpression(dscope, dscope, itarg->value.get());
                    if (!arg_ex) {
                        /* there's an invalid value for the argument */
                        return AnalyseResult{
                                std::string{}
                                + "invalid value for argument at " + itarg->at.to_string(),
                                AnalyseError{},
                                arg_ex};
                    }
                }

                if (itvar != std::end(vars)) {
                    std::stringstream ss{};
                    /* some variables are missing arguments */
                    for (;itvar != std::end(vars); ++itvar) {
                        ss << " ." << itvar->identifier;
                    }
                    return AnalyseResult{
                            std::string{}
                            + "arguments missing of domain `"
                            + (*dom)->identifier + "' for variables `"
                            + ss.str() + "' in expression at " + expression.at.to_string(),
                            AnalyseError{}};
                }

                if (itarg != std::end(args)) {
                    std::stringstream ss{};
                    /* too many arguments supplied */
                    for (;itarg != std::end(args); ++itarg) {
                        ss << " ." << itarg->identifier;
                    }
                    return AnalyseResult{
                            std::string{}
                            + "unexpected arguments of domain `"
                            + (*dom)->identifier + "' for `"
                            + ss.str() + "' in expression at " + expression.at.to_string(),
                            AnalyseError{}};
                }

                /* check for sub-domain lookup */
                auto sub_lookup_scope = std::make_shared<DomainScope>(
                        DomainScope{dscope->root, *dom, DomainScope::DOMAIN_SCOPE_FULL});
                auto sub_lookup = analyseExpression(
                        dscope, sub_lookup_scope, expression.lookup.get());
                if (!sub_lookup) {

                    /* lookup failed */
                    return AnalyseResult{
                            std::string{}
                            + "unexpected lookup in domain `"
                            + (*dom)->identifier + "' in expression at "
                            + expression.at.to_string(),
                            AnalyseError{},
                            sub_lookup};
                }

                return AnalyseResult{nullptr};
            }

        } else {
            if (!var->value.identifier.empty()) {
                /* that variable is value bounded */
                auto var_ex = analyseExpression(dscope, dscope, &var->value);
                if (!var_ex) {
                    return AnalyseResult{
                            std::string{}
                            + "invalid value constraint",
                            AnalyseError{},
                            var_ex};
                }
            }

            /* check domain bounded */

            return AnalyseResult{nullptr};
        }
    }
};


#endif // CS_FE_R_ANALYSER_HPP