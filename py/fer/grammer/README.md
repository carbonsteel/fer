# fer.grammer grammar reference

Note: The actual grammar is hard coded in python (see grammar.py).

```
token <expr> := /[ \n]*/ <expr>

# A grammar is a list of definitions. The root definition of the generated 
#   parser is the first definition occuring in the grammar file.
<root> := <definition>*

# Each definition is named, valued and optionaly hooked
<definition> := token(/\./) <identifier> <definition-value> <definition-hook>?

# Names may contain letters, underscores and hyphens only
<identifier> := token(/[a-zA-Z-_]+/)

# A value is either one of a regex class, a string literal, a mix of other
#   definitions or an alternative of other definitions
<definition-value> := <class> | <literal> | <composite> | <alternative>

# Classes use python's re module for character classes
<class> := token(/\[/) {any valid python re character class} /\]/

# Literals are, plain single-quoted strings
<literal> := token(/'/) /.+'/

# Composites use expressions inspired of regular expression to combine other
#   grammar definitions with optional multiplicities and anchors with which the
#   parser will define python classes in which to store parsed values. Generated
#   python classes will use the camel-translated name of the definition (ie:
#   my-def -> MyDef)
<composite> := token(/\(/) <composite-expression>+ token(/\)/)

# A composite expression refers by name to another grammar definition that 
#   must be parsed as part of the composite. 
# Directly following the name, regex-like quantifiers (plus, star, 
#   question-mark) may be applied which will, respectively, require at least 
#   one occurence, any number of occurences, and at most one occurence of the 
#   preceding definition. 
# Directly following the quantifiers, anchors may be applied.
<composite-expression> := <identifier> <expression-quantifier> <expression-anchor>?
<expression-quantifier> := /[\+\*\?]/?

# Anchors will map parsed values to fields in python objects corresponding to 
#   the complete composite definition. 
# A single anchor @ will create a field using the snake-translated name of the
#   definition. (ie: my-def -> my_def)
# A double anchor @@ will use the parsed value as the value of the current 
#   composite. A double anchor must be the only anchor of a composite. 
#   Composites using a double anchor must be defined after the definition they 
#   refer to.
# A named anchor @id will create a field for the expression using the name 
#   following the anchor. A named anchor may not use the name _fcrd, it is 
#   reserved to store coordinates at which the instance was found.
<expression-anchor> := /@/ (/@/ | <identifier>)?

# An alternative is a left-to-right list of definition which the parser will 
#   try to parse in the same order. The first definition to succeed is returned.
<alternative> := token(/{/) <identifier>+ token(/}/)

# A definition hook will be compiled as an hookable event in the parser's 
#   python code which will be fired after the definition's parser as returned. 
# Hook callbacks are given two parameters, first the value returned by the 
#   definition's parser and second an optional context passed by the 
#   registering code. Callbacks must return a ParseResult.
<definition-hook> := token(/:/) <identifier>
```