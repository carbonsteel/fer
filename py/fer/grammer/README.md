# fer.grammer reference

`fer.grammer` is a library inspired by Haskell's parsec library of combinatory parsers. It provides an LL(*) modular recursive descent parser as well as a compiler capable of generating parsers from a grammar definition syntax. It has been written for the sole purpose of automatically providing rich contextual error messages.

## grammar definitions

Note: The actual grammar is hard coded in python (see grammar.py).

```
token <expr> := /[ \n]*/ <expr>
```

1. A grammar is a list of definitions. The root definition of the generated 
   parser is the first definition occuring in the grammar file. 
   * `<root> := <definition>*`


1. Each definition is named, valued and optionaly hooked.
   * `<definition> := token(/\./) <identifier> <definition-value> <definition-hook>?`

1. Names may contain letters, underscores and hyphens only.
   * `<identifier> := token(/[a-zA-Z-_]+/)`

1. A value is either one of a regex class, a string literal, a mix of other
   definitions or an alternative of other definitions.
   * `<definition-value> := <class> | <literal> | <composite> | <alternative>`

1. Classes use python's re module for character classes.
   1. Embeded closing square brackets and dots must be repetition-escaped (ie: `']]'` == `"]"`, `'..'` == `"."`)
   1. Python escape sequences are accepted.
   * `<class> := token(/\[/) {any valid python re character class} /\]/`

1. Literals are, plain single-quoted strings.
   1. Embeded single quotes and dots must be repetition-escaped (ie: `''''` == `"'"`, `'..'` == `"."`)
   1. Python escape sequences are accepted.
   * `<literal> := token(/'/) /.+'/`

1. Composites use expressions inspired of regular expression to combine other
   grammar definitions with optional multiplicities and anchors with which the
   compiler will define python classes in which to store parsed values.
   Generated python classes will use the camel-translated name of the 
   definition (ie: `my-def` -> `MyDef`)
   * `<composite> := token(/\(/) <composite-expression>+ token(/\)/)`

1. A composite expression refers by name to another grammar definition that 
   must be parsed in left-to-right order as part of the composite. 
   1. Directly following the name, regex-like quantifiers (plus, star, 
   question-mark, brackets) may be applied which will, respectively, require at
   least one occurence, any number of occurences, at most one occurence of 
   the preceding definition. Brackets {n}, {n,}, {n,m} requires exactly n, at
   least n and at least n and up to m occurences.
   1. Directly following the quantifiers, anchors may be applied.
   * `<composite-expression> := <identifier> /({\d+(,|,\d+)}|[\+\*\?]?)/ <expression-anchor>?`

1. Anchors will map parsed values to fields in python objects corresponding to 
   the complete composite definition. 
   1. A single anchor `@` will create a field using the snake-translated name of the
   definition. (ie: `my-def` -> `my_def`)
   1. A double anchor `@@` will use the parsed value as the value of the current 
   composite. A double anchor must be the only anchor of a composite. 
   Composites using a double anchor must be defined after the definition they 
   refer to.
   1. A named anchor `@id` will create a field for the expression using the name 
   following the anchor. A named anchor may not use the name `_fcrd`, it is 
   reserved to store coordinates at which the instance was found.
   * `<expression-anchor> := /@/ (/@/ | <identifier>)?`

1. An alternative is a left-to-right list of definitions which the parser will 
   try to parse and return the first one to succeed.
   * `<alternative> := token(/{/) <identifier>+ token(/}/)`

1. A definition hook will be compiled as an event in the parser's 
   python code which will be fired after the definition's parser has returned. 
   1. Hook callbacks are given two parameters, first the value returned by the 
   definition's parser and second an optional context passed by the 
   registering code. Callbacks must return a ParseResult.
   * `<definition-hook> := token(/:/) <identifier>`


# References

http://web.archive.org/web/20170728155101/https://softwareengineering.stackexchange.com/questions/338665/when-to-use-a-parser-combinator-when-to-use-a-parser-generator
