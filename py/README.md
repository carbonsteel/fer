# grammar.py GrammarParser grammar

Note: intentionnaly not expressed in a compatible format to prevent confusion as to
the source of the semantics. The actual grammar is hard coded in the
python file. The below expressions are for documentative and referencial purposes
only.

    token <expr> := /[ \n]*/ <expr>
    <root> := <definition>*
    <definition> := token(/\./) <definition-content>
    <definition-content> := <definition-id> <definition-value>
    <definition-id> := <identifier>
    <identifier> := /[a-zA-Z-_]+/
    <definition-value> := <class> | <literal> | <composite>
    <class> := token(/\[/) <class-ccls> token(/\]/)
    <class-ccls> := {any valid python re character class}
    <literal> := token(/'/) <literal-literal> token(/'/)
    <literal-literal> := /.+/
    <composite> := token(/\(/) <composite-expression>+ token(/\(/)
    <composite-expression> := <expression-identifier> <expression-quantifier> <expression-anchor>?
    <expression-identifier> := <identifier>
    <expression-quantifier> := /[\+\*\?]/?
    <expression-anchor> := /@/ (/@/ | <identifier>)?