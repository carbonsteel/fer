#include <iostream>
#include <string>
#include <vector>

#include <cs/fe/parser.hpp>
#include <cs/fe/syntax/realm.hpp>

using namespace std;


using Parser = Parser_<char>;

class Interpreter {

};

void test_two() {
    cout << RealmDefinition<Parser>::parse({"two.fer"}).to_string() << endl;
}

int main(int argc, char **argv) {
    using Args = vector<string>;
    auto args = Args{argv, argv + argc};
    test_two();
}