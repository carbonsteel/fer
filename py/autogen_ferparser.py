# AUTOMATICLY GENERATED FILE.
# ALL CHANGES TO THIS FILE WILL BE DISCARDED.
# Updated on 2017-05-10 16:39:08.740943
from fer.grammer import *
# Classes
class Realm(object):
  def __init__(self, **args):
    StrictNamedArguments({'domains': {}, '_fcrd': {}})(self, args)
Ws = str
PseudoLetter = str
Dot = str
Domain = str
LeftCurlyBracket = str
RightCurlyBracket = str
VerticalLine = str
Colon = str
GreaterThanSign = str
EqualsSign = str
DollarSign = str
LeftParenthesis = str
RightParenthesis = str
Tilde = str
Solidus = str
PercentSign = str
Octothorp = str
LineFeed = str
LineCommentContent = str
W = str
LineComment = str
VariablePrefix = str
class RealmDomainDeclaration(object):
  def __init__(self, **args):
    StrictNamedArguments({'_fcrd': {}, 'domain_declaration': {}})(self, args)
class DomainDeclaration(object):
  def __init__(self, **args):
    StrictNamedArguments({'domain': {}, '_fcrd': {}, 'id': {}, 'result': {}})(self, args)
class DomainDefinition(object):
  def __init__(self, **args):
    StrictNamedArguments({'domains': {}, 'variables': {}, 'transforms': {}, '_fcrd': {}})(self, args)
class VariableDefinition(object):
  def __init__(self, **args):
    StrictNamedArguments({'domain': {}, 'id': {}, '_fcrd': {}})(self, args)
class Expression(object):
  def __init__(self, **args):
    StrictNamedArguments({'_fcrd': {}, 'lookup': {}, 'id': {}, 'arguments': {}})(self, args)
class ExpressionArgument(object):
  def __init__(self, **args):
    StrictNamedArguments({'expression': {}, 'id': {}, '_fcrd': {}})(self, args)
class VariableConstraint(object):
  def __init__(self, **args):
    StrictNamedArguments({'expression': {}, 'id': {}, '_fcrd': {}})(self, args)
class TransformDefinition(object):
  def __init__(self, **args):
    StrictNamedArguments({'expression': {}, '_fcrd': {}, 'locals': {}, 'constraints': {}})(self, args)
Id = str
InnerDomainDeclaration = DomainDeclaration
ExpressionArguments = list
ExpressionLookup = Expression
VariableDomain = Expression
# Main parser
class FerParser(object):
  def __init__(self, reader):
    self._reader = reader
  def __call__(self):
    return self.parse_realm()
  def parse_realm(self):
    return self._reader.parse_type(
      result_type=Realm,
      error='expected realm',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseResult(value=self._reader.get_coord(), coord=ParserCoord())),
        ('domains', 'expected realm-domain-declaration in realm', lambda: self._reader.parse_many_wp(self.parse_realm_domain_declaration, 1, 9223372036854775807)),
        ('', 'expected eof', self._reader.consume_eof),
      ])
  def parse_ws(self):
    return self._reader.parse_type(
      result_type=Ws,
      error='expected ws',
      parsers=[
        ('_fimm', 'expected ws', lambda: self._reader.consume_string(SimpleClassPredicate(' \n'), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_pseudo_letter(self):
    return self._reader.parse_type(
      result_type=PseudoLetter,
      error='expected pseudo-letter',
      parsers=[
        ('_fimm', 'expected pseudo-letter', lambda: self._reader.consume_string(SimpleClassPredicate('a-zA-Z_'), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_dot(self):
    return self._reader.parse_type(
      result_type=Dot,
      error='expected dot',
      parsers=[
        ('_fimm', 'expected dot', lambda: self._reader.consume_string(StringPredicate('.'), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_domain(self):
    return self._reader.parse_type(
      result_type=Domain,
      error='expected domain',
      parsers=[
        ('_fimm', 'expected domain', lambda: self._reader.consume_string(StringPredicate('domain'), 6, 6))
      ],
      result_immediate='_fimm')
  def parse_left_curly_bracket(self):
    return self._reader.parse_type(
      result_type=LeftCurlyBracket,
      error='expected left-curly-bracket',
      parsers=[
        ('_fimm', 'expected left-curly-bracket', lambda: self._reader.consume_string(StringPredicate('{'), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_right_curly_bracket(self):
    return self._reader.parse_type(
      result_type=RightCurlyBracket,
      error='expected right-curly-bracket',
      parsers=[
        ('_fimm', 'expected right-curly-bracket', lambda: self._reader.consume_string(StringPredicate('}'), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_vertical_line(self):
    return self._reader.parse_type(
      result_type=VerticalLine,
      error='expected vertical-line',
      parsers=[
        ('_fimm', 'expected vertical-line', lambda: self._reader.consume_string(StringPredicate('|'), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_colon(self):
    return self._reader.parse_type(
      result_type=Colon,
      error='expected colon',
      parsers=[
        ('_fimm', 'expected colon', lambda: self._reader.consume_string(StringPredicate(':'), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_greater_than_sign(self):
    return self._reader.parse_type(
      result_type=GreaterThanSign,
      error='expected greater-than-sign',
      parsers=[
        ('_fimm', 'expected greater-than-sign', lambda: self._reader.consume_string(StringPredicate('>'), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_equals_sign(self):
    return self._reader.parse_type(
      result_type=EqualsSign,
      error='expected equals-sign',
      parsers=[
        ('_fimm', 'expected equals-sign', lambda: self._reader.consume_string(StringPredicate('='), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_dollar_sign(self):
    return self._reader.parse_type(
      result_type=DollarSign,
      error='expected dollar-sign',
      parsers=[
        ('_fimm', 'expected dollar-sign', lambda: self._reader.consume_string(StringPredicate('$'), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_left_parenthesis(self):
    return self._reader.parse_type(
      result_type=LeftParenthesis,
      error='expected left-parenthesis',
      parsers=[
        ('_fimm', 'expected left-parenthesis', lambda: self._reader.consume_string(StringPredicate('('), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_right_parenthesis(self):
    return self._reader.parse_type(
      result_type=RightParenthesis,
      error='expected right-parenthesis',
      parsers=[
        ('_fimm', 'expected right-parenthesis', lambda: self._reader.consume_string(StringPredicate(')'), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_tilde(self):
    return self._reader.parse_type(
      result_type=Tilde,
      error='expected tilde',
      parsers=[
        ('_fimm', 'expected tilde', lambda: self._reader.consume_string(StringPredicate('~'), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_solidus(self):
    return self._reader.parse_type(
      result_type=Solidus,
      error='expected solidus',
      parsers=[
        ('_fimm', 'expected solidus', lambda: self._reader.consume_string(StringPredicate('/'), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_percent_sign(self):
    return self._reader.parse_type(
      result_type=PercentSign,
      error='expected percent-sign',
      parsers=[
        ('_fimm', 'expected percent-sign', lambda: self._reader.consume_string(StringPredicate('%'), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_octothorp(self):
    return self._reader.parse_type(
      result_type=Octothorp,
      error='expected octothorp',
      parsers=[
        ('_fimm', 'expected octothorp', lambda: self._reader.consume_string(StringPredicate('#'), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_line_feed(self):
    return self._reader.parse_type(
      result_type=LineFeed,
      error='expected line-feed',
      parsers=[
        ('_fimm', 'expected line-feed', lambda: self._reader.consume_string(StringPredicate('\n'), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_line_comment_content(self):
    return self._reader.parse_type(
      result_type=LineCommentContent,
      error='expected line-comment-content',
      parsers=[
        ('_fimm', 'expected line-comment-content', lambda: self._reader.consume_string(SimpleClassPredicate('^\n'), 1, 1))
      ],
      result_immediate='_fimm')
  def parse_w(self):
    return self._reader.parse_type(
      result_type=W,
      error='expected w',
      parsers=[
        ('', 'expected ws in w', lambda: self._reader.consume_string(SimpleClassPredicate(' \n'), 0, 9223372036854775807)),
        ('', 'expected line-comment in w', lambda: self._reader.parse_many_wp(self.parse_line_comment, 0, 1)),
        ('', 'expected ws in w', lambda: self._reader.consume_string(SimpleClassPredicate(' \n'), 0, 9223372036854775807)),
      ])
  def parse_line_comment(self):
    return self._reader.parse_type(
      result_type=LineComment,
      error='expected line-comment',
      parsers=[
        ('', 'expected octothorp in line-comment', self.parse_octothorp),
        ('', 'expected line-comment-content in line-comment', lambda: self._reader.consume_string(SimpleClassPredicate('^\n'), 0, 9223372036854775807)),
        ('', 'expected line-feed in line-comment', self.parse_line_feed),
      ])
  def parse_id(self):
    return self._reader.parse_type(
      result_type=Id,
      error='expected id',
      parsers=[
        ('', 'expected w in id', self.parse_w),
        ('_fimm', 'expected pseudo-letter in id', lambda: self._reader.consume_string(SimpleClassPredicate('a-zA-Z_'), 1, 9223372036854775807)),
      ],
      result_immediate='_fimm')
  def parse_variable_prefix(self):
    return self._reader.parse_type(
      result_type=VariablePrefix,
      error='expected variable-prefix',
      parsers=[
        ('', 'expected w in variable-prefix', self.parse_w),
        ('', 'expected dot in variable-prefix', self.parse_dot),
      ])
  def parse_realm_domain_declaration(self):
    return self._reader.parse_type(
      result_type=RealmDomainDeclaration,
      error='expected realm-domain-declaration',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseResult(value=self._reader.get_coord(), coord=ParserCoord())),
        ('', 'expected w in realm-domain-declaration', self.parse_w),
        ('', 'expected domain in realm-domain-declaration', self.parse_domain),
        ('domain_declaration', 'expected domain-declaration in realm-domain-declaration', self.parse_domain_declaration),
      ])
  def parse_domain_declaration(self):
    return self._reader.parse_type(
      result_type=DomainDeclaration,
      error='expected domain-declaration',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseResult(value=self._reader.get_coord(), coord=ParserCoord())),
        ('id', 'expected id in domain-declaration', self.parse_id),
        ('result', 'expected variable-domain in domain-declaration', lambda: self._reader.parse_many_wp(self.parse_variable_domain, 0, 1)),
        ('domain', 'expected domain-definition in domain-declaration', lambda: self._reader.parse_many_wp(self.parse_domain_definition, 0, 1)),
      ])
  def parse_domain_definition(self):
    return self._reader.parse_type(
      result_type=DomainDefinition,
      error='expected domain-definition',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseResult(value=self._reader.get_coord(), coord=ParserCoord())),
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
      result_type=InnerDomainDeclaration,
      error='expected inner-domain-declaration',
      parsers=[
        ('', 'expected w in inner-domain-declaration', self.parse_w),
        ('', 'expected vertical-line in inner-domain-declaration', self.parse_vertical_line),
        ('_fimm', 'expected domain-declaration in inner-domain-declaration', self.parse_domain_declaration),
      ],
      result_immediate='_fimm')
  def parse_variable_definition(self):
    return self._reader.parse_type(
      result_type=VariableDefinition,
      error='expected variable-definition',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseResult(value=self._reader.get_coord(), coord=ParserCoord())),
        ('', 'expected variable-prefix in variable-definition', self.parse_variable_prefix),
        ('id', 'expected id in variable-definition', self.parse_id),
        ('domain', 'expected variable-domain in variable-definition', lambda: self._reader.parse_many_wp(self.parse_variable_domain, 0, 1)),
      ])
  def parse_expression(self):
    return self._reader.parse_type(
      result_type=Expression,
      error='expected expression',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseResult(value=self._reader.get_coord(), coord=ParserCoord())),
        ('id', 'expected id in expression', self.parse_id),
        ('arguments', 'expected expression-arguments in expression', lambda: self._reader.parse_many_wp(self.parse_expression_arguments, 0, 1)),
        ('lookup', 'expected expression-lookup in expression', lambda: self._reader.parse_many_wp(self.parse_expression_lookup, 0, 1)),
      ])
  def parse_expression_argument(self):
    return self._reader.parse_type(
      result_type=ExpressionArgument,
      error='expected expression-argument',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseResult(value=self._reader.get_coord(), coord=ParserCoord())),
        ('', 'expected variable-prefix in expression-argument', self.parse_variable_prefix),
        ('id', 'expected id in expression-argument', self.parse_id),
        ('', 'expected w in expression-argument', self.parse_w),
        ('', 'expected tilde in expression-argument', self.parse_tilde),
        ('expression', 'expected expression in expression-argument', self.parse_expression),
      ])
  def parse_expression_arguments(self):
    return self._reader.parse_type(
      result_type=ExpressionArguments,
      error='expected expression-arguments',
      parsers=[
        ('', 'expected w in expression-arguments', self.parse_w),
        ('', 'expected left-parenthesis in expression-arguments', self.parse_left_parenthesis),
        ('_fimm', 'expected expression-argument in expression-arguments', lambda: self._reader.parse_many_wp(self.parse_expression_argument, 1, 9223372036854775807)),
        ('', 'expected w in expression-arguments', self.parse_w),
        ('', 'expected right-parenthesis in expression-arguments', self.parse_right_parenthesis),
      ],
      result_immediate='_fimm')
  def parse_expression_lookup(self):
    return self._reader.parse_type(
      result_type=ExpressionLookup,
      error='expected expression-lookup',
      parsers=[
        ('', 'expected w in expression-lookup', self.parse_w),
        ('', 'expected solidus in expression-lookup', self.parse_solidus),
        ('_fimm', 'expected expression in expression-lookup', self.parse_expression),
      ],
      result_immediate='_fimm')
  def parse_variable_domain(self):
    return self._reader.parse_type(
      result_type=VariableDomain,
      error='expected variable-domain',
      parsers=[
        ('', 'expected colon in variable-domain', self.parse_colon),
        ('_fimm', 'expected expression in variable-domain', self.parse_expression),
      ],
      result_immediate='_fimm')
  def parse_variable_constraint(self):
    return self._reader.parse_type(
      result_type=VariableConstraint,
      error='expected variable-constraint',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseResult(value=self._reader.get_coord(), coord=ParserCoord())),
        ('', 'expected variable-prefix in variable-constraint', self.parse_variable_prefix),
        ('id', 'expected id in variable-constraint', self.parse_id),
        ('', 'expected equals-sign in variable-constraint', self.parse_equals_sign),
        ('expression', 'expected expression in variable-constraint', self.parse_expression),
      ])
  def parse_transform_definition(self):
    return self._reader.parse_type(
      result_type=TransformDefinition,
      error='expected transform-definition',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseResult(value=self._reader.get_coord(), coord=ParserCoord())),
        ('', 'expected w in transform-definition', self.parse_w),
        ('', 'expected greater-than-sign in transform-definition', self.parse_greater_than_sign),
        ('constraints', 'expected variable-constraint in transform-definition', lambda: self._reader.parse_many_wp(self.parse_variable_constraint, 0, 9223372036854775807)),
        ('', 'expected w in transform-definition', self.parse_w),
        ('', 'expected dollar-sign in transform-definition', self.parse_dollar_sign),
        ('locals', 'expected expression-argument in transform-definition', lambda: self._reader.parse_many_wp(self.parse_expression_argument, 0, 9223372036854775807)),
        ('expression', 'expected expression in transform-definition', self.parse_expression),
      ])
