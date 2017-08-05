#include <iostream>
#include <string>
#include <vector>

#include <cs/fe/parser.hpp>
#include <cs/fe/r.hpp>

using namespace std;


using Parser = Parser_<char>;
/*

        auto is_main = [](const DomainType &domain) -> bool {
            return domain.identifier == std::string{"Main"};
        }
        auto it = std::find_if(std::begin(realm.domains), std::end(realm.domains), is_main);
        if (it == std::end(realm.domains)) {
            return Result{
                    std::string{}
                    + "expected domain-of-the-realm named `Main' as program point-of-entry",
                    IsError{}};
        }

        
        return Result{realm};
        */

void test_two() {
    auto parse_result = RealmDefinition<Parser>::parse({"two.fer"});
    cout << "syntax " << parse_result.to_string() << endl;
    if (!parse_result) {
        return;
    }

    Analyser<Parser> analyser{};
    auto analyse_result = analyser.analyse(parse_result.result);
    cout << "semantics " << analyse_result.to_string() << endl;
}

int main(int argc, char **argv) {
    using Args = vector<string>;
    auto args = Args{argv, argv + argc};
    test_two();
}