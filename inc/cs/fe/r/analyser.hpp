#ifndef CS_FE_R_ANALYSER_HPP
#define CS_FE_R_ANALYSER_HPP

#include <algorithm>
#include <string>

#include <cs/fe/syntax/realm.hpp>


/* checks for semantic integrity of a parsed realm */
template <class Tparser>
class Analyser {
    using RealmType = RealmDefinition<Tparser>;
    using DomainType = typename RealmType::DomainDefinitionType;
    using VariableType = typename DomainType::VariableDefinition;
    using TransformType = typename DomainType::TransformDefinition;
    using ExpressionType = typename TransformType::ExpressionDefinition;
    using ArgumentType = typename ExpressionType::ArgumentDefinition;
    using AnalyseResult = ParseResult<void*>;
    using AnalyseError = typename AnalyseResult::IsError;

public:
    auto analyse(const RealmType &realm) {
        RealmType rscope{};
        AnalyseResult domains_check;
        for (const auto &d : realm.domains) {
            auto domain_check = analyseDomain(rscope, d);
            domains_check.merge(domain_check);
        }
        if (!domains_check) {
            return domains_check;
        }

        return AnalyseResult{nullptr};
    }
    auto analyseDomain(RealmType &rscope, const DomainType &domain) {
        DomainType dscope{};
        AnalyseResult variables_check;
        for (const auto &v : domain.variables) {
            auto var_check = analyseVariable(dscope, v);
            variables_check.merge(var_check);
        }
        if (!variables_check) {
            return variables_check;
        }
        rscope.domains.push_back(dscope);

        return AnalyseResult{nullptr};
    }
    auto analyseVariable(DomainType &dscope, const VariableType &variable) {
        auto same_identifier = [&](const VariableType &v) -> bool {
            return v.identifier == variable.identifier;
        };
        auto it = std::find_if(std::begin(dscope.variables), std::end(dscope.variables), same_identifier);
        if (it != std::end(dscope.variables)) {
            return AnalyseResult{
                    std::string{}
                    + "redeclaration of variable `" + variable.identifier + "' from " + it->at.to_string() + " at " + variable.at.to_string(),
                    AnalyseError{}};
        }

        dscope.variables.push_back(variable);

        return AnalyseResult{nullptr};
    }
    auto analyseExpression(const RealmType &scope, const ExpressionType &expression) {
        return AnalyseResult{nullptr};
    }
};


#endif // CS_FE_R_ANALYSER_HPP