#ifndef CS_FE_R_ANALYSER_HPP
#define CS_FE_R_ANALYSER_HPP

#include <algorithm>
#include <iterator>
#include <string>

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

    struct DomainScope {
        const DomainPtrType &domain;
        using VariableConstIteratorType = typename decltype(domain->variables)::const_iterator;
        const VariableConstIteratorType vbegin;
        const VariableConstIteratorType vend;
        VariableConstIteratorType vs;
        using DomainConstIteratorType = typename decltype(domain->domains)::const_iterator;
        const DomainConstIteratorType dbegin;
        const DomainConstIteratorType dend;
        DomainConstIteratorType ds;
        DomainScope(const DomainPtrType &domain)
                : domain{domain},
                  vbegin{std::cbegin(domain->variables)},
                  vend{std::cend(domain->variables)}, vs{vbegin},
                  dbegin{std::cbegin(domain->domains)},
                  dend{std::cend(domain->domains)}, ds{dbegin} {}
    };
    using AnalyseResult = ParseResult<void*>;
    using AnalyseError = typename AnalyseResult::IsError;

public:
    auto analyse(const RealmType &realm) {
        DomainScope dscope{realm.domain};
        return analyseDomain(dscope);
    }
    AnalyseResult analyseDomain(DomainScope &dscope) {
        std::cout << "analyseDomain " << dscope.domain->identifier << std::endl;  
        AnalyseResult variables_check;
        for (; dscope.vs != dscope.vend; ++dscope.vs) {
            auto var_check = analyseVariable(dscope);
            variables_check.merge(var_check);
        }
        if (!variables_check) {
            return variables_check;
        }

        AnalyseResult domains_check;
        for (; dscope.ds != dscope.dend; ++dscope.ds) {
            DomainScope sdscope{*dscope.ds};
            auto domain_check = analyseDomain(sdscope);
            domains_check.merge(domain_check);
        }
        if (!domains_check) {
            return domains_check;
        }

        return AnalyseResult{nullptr};
    }

    AnalyseResult analyseVariable(const DomainScope &dscope) {
        std::cout << "analyseVariable " << dscope.vs->identifier << std::endl;  
        auto same_identifier = [&](const VariableType &v) -> bool {
            return v.identifier == dscope.vs->identifier;
        };
        auto it = std::find_if(dscope.vbegin, dscope.vs, same_identifier);
        if (it != dscope.vs) {
            return AnalyseResult{
                    std::string{}
                    + "redeclaration of variable `" + dscope.vs->identifier 
                    + "' from " + it->at.to_string() + " at " + dscope.vs->at.to_string(),
                    AnalyseError{}};
        }

        if (!dscope.vs->value.identifier.empty()) {
          auto value_ex = analyseExpression(dscope, dscope.vs->value);
          if (!value_ex) {
              return AnalyseResult{
                      std::string{}
                      + "unexpected variable value at " + dscope.vs->value.at.to_string(),
                      AnalyseError{},
                      value_ex};
          }
        }

        if (!dscope.vs->domain.identifier.empty()) {
          auto domain_ex = analyseExpression(dscope, dscope.vs->domain);
          if (!domain_ex) {
              return AnalyseResult{
                      std::string{}
                      + "unexpected variable domain at " + dscope.vs->domain.at.to_string(),
                      AnalyseError{},
                      domain_ex};
          }
        }

        /* check for conflicting value and domain bounds */

        return AnalyseResult{nullptr};
    }

    AnalyseResult analyseExpression(const DomainScope &dscope, const ExpressionType &expression) {
        std::cout << "analyseExpression " << expression.to_string() << std::endl;  
        auto var_identifier = [&](const VariableType &v) -> bool {
            return v.identifier == expression.identifier;
        };
        auto var = std::find_if(dscope.vbegin, dscope.vs, var_identifier);
        /* expression is refering to a variable */
        if (var != dscope.vs) {
            /* that variable is value bounded */
            if (!var->value.identifier.empty()) {
                auto var_ex = analyseExpression(dscope, var->value);
                if (!var_ex) {
                    return AnalyseResult{
                            std::string{}
                            + "invalid value constraint at " + var->value.at.to_string(),
                            AnalyseError{},
                            var_ex};
                }
/*
                auto domain_identifier = [&](const DomainType &d) -> bool {
                    return d.identifier == var->value.identifier;
                };
                auto var = std::find_if(std::begin(dscope.variables), std::end(dscope.variables), domain_identifier);*/
            }
        }
        return AnalyseResult{nullptr};
    }
};


#endif // CS_FE_R_ANALYSER_HPP