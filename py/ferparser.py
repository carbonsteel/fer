# AUTOMATICLY GENERATED FILE.
# ALL CHANGES TO THIS FILE WILL BE DISCARDED.
import grammar
# Classes
class RealmDefinition(object):
  def __init__(self, **args):
    grammar.StrictNamedArguments({'domains': {}})(self, args)
WsDefinition = str
PseudoLetterDefinition = str
DotDefinition = str
DomainDefinition = str
LeftCurlyBracketDefinition = str
RightCurlyBracketDefinition = str
VerticalLineDefinition = str
ColonDefinition = str
GreaterThanSignDefinition = str
EqualsSignDefinition = str
DollarSignDefinition = str
LeftParenthesisDefinition = str
RightParenthesisDefinition = str
TildeDefinition = str
SolidusDefinition = str
PercentSignDefinition = str
WDefinition = str
VariablePrefixDefinition = str
class RealmDomainDeclarationDefinition(object):
  def __init__(self, **args):
    grammar.StrictNamedArguments({'domain_declaration': {}})(self, args)
class DomainDeclarationDefinition(object):
  def __init__(self, **args):
    grammar.StrictNamedArguments({'domain': {}, 'id': {}})(self, args)
class DomainDefinitionDefinition(object):
  def __init__(self, **args):
    grammar.StrictNamedArguments({'domains': {}, 'variables': {}, 'transforms': {}})(self, args)
InnerDomainDeclarationDefinition = str
class VariableDefinitionDefinition(object):
  def __init__(self, **args):
    grammar.StrictNamedArguments({'expression': {}, 'id': {}})(self, args)
class VariableConstraintDefinition(object):
  def __init__(self, **args):
    grammar.StrictNamedArguments({'expression': {}, 'id': {}})(self, args)
class TransformDefinitionDefinition(object):
  def __init__(self, **args):
    grammar.StrictNamedArguments({'expression': {}, 'locals': {}, 'constraints': {}})(self, args)
class ExpressionDefinition(object):
  def __init__(self, **args):
    grammar.StrictNamedArguments({'lookup': {}, 'id': {}, 'arguments': {}})(self, args)
class ExpressionArgumentDefinition(object):
  def __init__(self, **args):
    grammar.StrictNamedArguments({'expression': {}, 'id': {}})(self, args)
IdDefinition = PseudoLetterDefinition
ExpressionArgumentsDefinition = ExpressionArgumentDefinition
ExpressionLookupDefinition = ExpressionDefinition
# Main parser
class FerParser(object):
  def __init__(self, reader):
    self._reader = reader
  def __call__(self):
    return self.parse_realm()
  def parse_realm(self):
    return self._reader.parse_type(
      result_type=RealmDefinition,
      error='expected realm',
      parsers=[
        ('domains', 'expected realm-domain-declaration in realm', lambda: self._reader.parse_many_wp(self.parse_realm_domain_declaration, 1, 9223372036854775807)),
      ])
  def parse_ws(self):
    return self._reader.parse_type(
      result_type=WsDefinition,
      error='expected ws',
      parsers=[
        ('_', 'expected ws', lambda: self._reader.consume_string(grammar.SimpleClassPredicate(' \\n'), 1, 1))
      ],
      result_immediate='_')
  def parse_pseudo_letter(self):
    return self._reader.parse_type(
      result_type=PseudoLetterDefinition,
      error='expected pseudo-letter',
      parsers=[
        ('_', 'expected pseudo-letter', lambda: self._reader.consume_string(grammar.SimpleClassPredicate('a-zA-Z_'), 1, 1))
      ],
      result_immediate='_')
  def parse_dot(self):
    return self._reader.parse_type(
      result_type=DotDefinition,
      error='expected dot',
      parsers=[
        ('_', 'expected dot', lambda: self._reader.consume_string(grammar.StringPredicate('.'), 1, 1))
      ],
      result_immediate='_')
  def parse_domain(self):
    return self._reader.parse_type(
      result_type=DomainDefinition,
      error='expected domain',
      parsers=[
        ('_', 'expected domain', lambda: self._reader.consume_string(grammar.StringPredicate('domain'), 6, 6))
      ],
      result_immediate='_')
  def parse_left_curly_bracket(self):
    return self._reader.parse_type(
      result_type=LeftCurlyBracketDefinition,
      error='expected left-curly-bracket',
      parsers=[
        ('_', 'expected left-curly-bracket', lambda: self._reader.consume_string(grammar.StringPredicate('{'), 1, 1))
      ],
      result_immediate='_')
  def parse_right_curly_bracket(self):
    return self._reader.parse_type(
      result_type=RightCurlyBracketDefinition,
      error='expected right-curly-bracket',
      parsers=[
        ('_', 'expected right-curly-bracket', lambda: self._reader.consume_string(grammar.StringPredicate('}'), 1, 1))
      ],
      result_immediate='_')
  def parse_vertical_line(self):
    return self._reader.parse_type(
      result_type=VerticalLineDefinition,
      error='expected vertical-line',
      parsers=[
        ('_', 'expected vertical-line', lambda: self._reader.consume_string(grammar.StringPredicate('|'), 1, 1))
      ],
      result_immediate='_')
  def parse_colon(self):
    return self._reader.parse_type(
      result_type=ColonDefinition,
      error='expected colon',
      parsers=[
        ('_', 'expected colon', lambda: self._reader.consume_string(grammar.StringPredicate(':'), 1, 1))
      ],
      result_immediate='_')
  def parse_greater_than_sign(self):
    return self._reader.parse_type(
      result_type=GreaterThanSignDefinition,
      error='expected greater-than-sign',
      parsers=[
        ('_', 'expected greater-than-sign', lambda: self._reader.consume_string(grammar.StringPredicate('>'), 1, 1))
      ],
      result_immediate='_')
  def parse_equals_sign(self):
    return self._reader.parse_type(
      result_type=EqualsSignDefinition,
      error='expected equals-sign',
      parsers=[
        ('_', 'expected equals-sign', lambda: self._reader.consume_string(grammar.StringPredicate('='), 1, 1))
      ],
      result_immediate='_')
  def parse_dollar_sign(self):
    return self._reader.parse_type(
      result_type=DollarSignDefinition,
      error='expected dollar-sign',
      parsers=[
        ('_', 'expected dollar-sign', lambda: self._reader.consume_string(grammar.StringPredicate('$'), 1, 1))
      ],
      result_immediate='_')
  def parse_left_parenthesis(self):
    return self._reader.parse_type(
      result_type=LeftParenthesisDefinition,
      error='expected left-parenthesis',
      parsers=[
        ('_', 'expected left-parenthesis', lambda: self._reader.consume_string(grammar.StringPredicate('('), 1, 1))
      ],
      result_immediate='_')
  def parse_right_parenthesis(self):
    return self._reader.parse_type(
      result_type=RightParenthesisDefinition,
      error='expected right-parenthesis',
      parsers=[
        ('_', 'expected right-parenthesis', lambda: self._reader.consume_string(grammar.StringPredicate(')'), 1, 1))
      ],
      result_immediate='_')
  def parse_tilde(self):
    return self._reader.parse_type(
      result_type=TildeDefinition,
      error='expected tilde',
      parsers=[
        ('_', 'expected tilde', lambda: self._reader.consume_string(grammar.StringPredicate('~'), 1, 1))
      ],
      result_immediate='_')
  def parse_solidus(self):
    return self._reader.parse_type(
      result_type=SolidusDefinition,
      error='expected solidus',
      parsers=[
        ('_', 'expected solidus', lambda: self._reader.consume_string(grammar.StringPredicate('/'), 1, 1))
      ],
      result_immediate='_')
  def parse_percent_sign(self):
    return self._reader.parse_type(
      result_type=PercentSignDefinition,
      error='expected percent-sign',
      parsers=[
        ('_', 'expected percent-sign', lambda: self._reader.consume_string(grammar.StringPredicate('%'), 1, 1))
      ],
      result_immediate='_')
  def parse_w(self):
    return self._reader.parse_type(
      result_type=WDefinition,
      error='expected w',
      parsers=[
        ('', 'expected ws in w', lambda: self._reader.parse_many_wp(self.parse_ws, 0, 9223372036854775807)),
      ])
  def parse_id(self):
    return self._reader.parse_type(
      result_type=IdDefinition,
      error='expected id',
      parsers=[
        ('', 'expected w in id', self.parse_w),
        ('_', 'expected pseudo-letter in id', lambda: self._reader.parse_many_wp(self.parse_pseudo_letter, 1, 9223372036854775807)),
      ],
      result_immediate='_')
  def parse_variable_prefix(self):
    return self._reader.parse_type(
      result_type=VariablePrefixDefinition,
      error='expected variable-prefix',
      parsers=[
        ('', 'expected w in variable-prefix', self.parse_w),
        ('', 'expected dot in variable-prefix', self.parse_dot),
      ])
  def parse_realm_domain_declaration(self):
    return self._reader.parse_type(
      result_type=RealmDomainDeclarationDefinition,
      error='expected realm-domain-declaration',
      parsers=[
        ('', 'expected w in realm-domain-declaration', self.parse_w),
        ('', 'expected domain in realm-domain-declaration', self.parse_domain),
        ('domain_declaration', 'expected domain-declaration in realm-domain-declaration', self.parse_domain_declaration),
      ])
  def parse_domain_declaration(self):
    return self._reader.parse_type(
      result_type=DomainDeclarationDefinition,
      error='expected domain-declaration',
      parsers=[
        ('id', 'expected id in domain-declaration', self.parse_id),
        ('domain', 'expected domain-definition in domain-declaration', lambda: self._reader.parse_many_wp(self.parse_domain_definition, 0, 1)),
      ])
  def parse_domain_definition(self):
    return self._reader.parse_type(
      result_type=DomainDefinitionDefinition,
      error='expected domain-definition',
      parsers=[
        ('', 'expected w in domain-definition', self.parse_w),
        ('', 'expected left-curly-bracket in domain-definition', self.parse_left_curly_bracket),
        ('variables', 'expected variable-definition in domain-definition', lambda: self._reader.parse_many_wp(self.parse_variable_definition, 0, 9223372036854775807)),
        ('domains', 'expected inner-domain-declaration in domain-definition', lambda: self._reader.parse_many_wp(self.parse_inner_domain_declaration, 0, 9223372036854775807)),
        ('transforms', 'expected transform-definition in domain-definition', lambda: self._reader.parse_many_wp(self.parse_transform_definition, 0, 9223372036854775807)),
        ('', 'expected w in domain-definition', self.parse_w),
        ('', 'expected right-curly-bracket in domain-definition', self.parse_right_curly_bracket),
      ])
  def parse_inner_domain_declaration(self):
    return self._reader.parse_type(
      result_type=InnerDomainDeclarationDefinition,
      error='expected inner-domain-declaration',
      parsers=[
        ('', 'expected w in inner-domain-declaration', self.parse_w),
        ('', 'expected vertical-line in inner-domain-declaration', self.parse_vertical_line),
        ('', 'expected domain-declaration in inner-domain-declaration', self.parse_domain_declaration),
      ])
  def parse_variable_definition(self):
    return self._reader.parse_type(
      result_type=VariableDefinitionDefinition,
      error='expected variable-definition',
      parsers=[
        ('', 'expected variable-prefix in variable-definition', self.parse_variable_prefix),
        ('id', 'expected id in variable-definition', self.parse_id),
        ('', 'expected colon in variable-definition', self.parse_colon),
        ('expression', 'expected expression in variable-definition', self.parse_expression),
      ])
  def parse_variable_constraint(self):
    return self._reader.parse_type(
      result_type=VariableConstraintDefinition,
      error='expected variable-constraint',
      parsers=[
        ('', 'expected variable-prefix in variable-constraint', self.parse_variable_prefix),
        ('id', 'expected id in variable-constraint', self.parse_id),
        ('', 'expected equals-sign in variable-constraint', self.parse_equals_sign),
        ('expression', 'expected expression in variable-constraint', self.parse_expression),
      ])
  def parse_transform_definition(self):
    return self._reader.parse_type(
      result_type=TransformDefinitionDefinition,
      error='expected transform-definition',
      parsers=[
        ('', 'expected w in transform-definition', self.parse_w),
        ('', 'expected greater-than-sign in transform-definition', self.parse_greater_than_sign),
        ('constraints', 'expected variable-constraint in transform-definition', lambda: self._reader.parse_many_wp(self.parse_variable_constraint, 0, 9223372036854775807)),
        ('', 'expected w in transform-definition', self.parse_w),
        ('', 'expected dollar-sign in transform-definition', self.parse_dollar_sign),
        ('locals', 'expected expression-argument in transform-definition', lambda: self._reader.parse_many_wp(self.parse_expression_argument, 0, 9223372036854775807)),
        ('expression', 'expected expression in transform-definition', self.parse_expression),
      ])
  def parse_expression(self):
    return self._reader.parse_type(
      result_type=ExpressionDefinition,
      error='expected expression',
      parsers=[
        ('id', 'expected id in expression', self.parse_id),
        ('arguments', 'expected expression-arguments in expression', lambda: self._reader.parse_many_wp(self.parse_expression_arguments, 0, 1)),
        ('lookup', 'expected expression-lookup in expression', lambda: self._reader.parse_many_wp(self.parse_expression_lookup, 0, 1)),
      ])
  def parse_expression_arguments(self):
    return self._reader.parse_type(
      result_type=ExpressionArgumentsDefinition,
      error='expected expression-arguments',
      parsers=[
        ('', 'expected w in expression-arguments', self.parse_w),
        ('', 'expected left-parenthesis in expression-arguments', self.parse_left_parenthesis),
        ('_', 'expected expression-argument in expression-arguments', lambda: self._reader.parse_many_wp(self.parse_expression_argument, 1, 9223372036854775807)),
        ('', 'expected w in expression-arguments', self.parse_w),
        ('', 'expected right-parenthesis in expression-arguments', self.parse_right_parenthesis),
      ],
      result_immediate='_')
  def parse_expression_argument(self):
    return self._reader.parse_type(
      result_type=ExpressionArgumentDefinition,
      error='expected expression-argument',
      parsers=[
        ('', 'expected variable-prefix in expression-argument', self.parse_variable_prefix),
        ('id', 'expected id in expression-argument', self.parse_id),
        ('', 'expected w in expression-argument', self.parse_w),
        ('', 'expected tilde in expression-argument', self.parse_tilde),
        ('expression', 'expected expression in expression-argument', self.parse_expression),
      ])
  def parse_expression_lookup(self):
    return self._reader.parse_type(
      result_type=ExpressionLookupDefinition,
      error='expected expression-lookup',
      parsers=[
        ('', 'expected w in expression-lookup', self.parse_w),
        ('', 'expected solidus in expression-lookup', self.parse_solidus),
        ('_', 'expected expression in expression-lookup', self.parse_expression),
      ],
      result_immediate='_')
