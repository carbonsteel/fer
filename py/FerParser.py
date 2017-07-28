# AUTOMATICLY GENERATED FILE.
# ALL CHANGES TO THIS FILE WILL BE DISCARDED.
# Updated on 2017-07-28 17:19:40.498987
from fer.grammer import *
# Classes
class Realm(object):
  def __init__(self, imports, domains, _fcrd):
    self.imports = imports
    self.domains = domains
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'domains', 'imports'], self, state)
Ws = str
PseudoLetter = str
Dot = str
DomainLiteralFull = str
DomainLiteralMin = str
From = str
ImportLiteralFull = str
ImportLiteralMin = str
As = str
LeftCurlyBracket = str
RightCurlyBracket = str
LeftSquareBracket = str
RightSquareBracket = str
VerticalLine = str
Colon = str
DoubleColon = str
GreaterThanSign = str
EqualsSign = str
DollarSign = str
Ampersand = str
LeftParenthesis = str
RightParenthesis = str
Tilde = str
Solidus = str
PercentSign = str
Octothorp = str
LineFeed = str
LineCommentContent = str
LeftToRightArrow = str
SingleQuote = str
DoubleQuote = str
Domain = idem
Import = idem
Ww = str
W = str
LineComment = str
VariablePrefix = str
class RealmPath(object):
  def __init__(self, local, path, _fcrd):
    self.local = local
    self.path = path
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'local', 'path'], self, state)
class RealmPathBranch(object):
  def __init__(self, realm, _fcrd):
    self.realm = realm
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'realm'], self, state)
class RealmDomainImport(object):
  def __init__(self, realm, domains, _fcrd):
    self.realm = realm
    self.domains = domains
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'domains', 'realm'], self, state)
class ImportDomain(object):
  def __init__(self, domain, as_domain, _fcrd):
    self.domain = domain
    self.as_domain = as_domain
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'as_domain', 'domain'], self, state)
class DomainDeclaration(object):
  def __init__(self, id, codomain, domain, _fcrd):
    self.id = id
    self.codomain = codomain
    self.domain = domain
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'codomain', 'domain', 'id'], self, state)
class DomainDefinition(object):
  def __init__(self, variables, domains, transforms, _fcrd):
    self.variables = variables
    self.domains = domains
    self.transforms = transforms
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'domains', 'transforms', 'variables'], self, state)
class Expression(object):
  def __init__(self, alt, _fcrd):
    self.alt = alt
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'alt'], self, state)
ExpressionAlt = idem
class ExpressionDomain(object):
  def __init__(self, domainof, id, arguments, lookup, _fcrd):
    self.domainof = domainof
    self.id = id
    self.arguments = arguments
    self.lookup = lookup
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'arguments', 'domainof', 'id', 'lookup'], self, state)
ExpressionLiteral = idem
ExpressionLiteralStringContent = str
class ExpressionArgument(object):
  def __init__(self, id, expression, _fcrd):
    self.id = id
    self.expression = expression
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'expression', 'id'], self, state)
VariableDefinition = idem
class VariableConstraints(object):
  def __init__(self, constraints, _fcrd):
    self.constraints = constraints
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'constraints'], self, state)
class VariableBound(object):
  def __init__(self, id, variable_domain, variable_constraints, _fcrd):
    self.id = id
    self.variable_domain = variable_domain
    self.variable_constraints = variable_constraints
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'id', 'variable_constraints', 'variable_domain'], self, state)
class VariableConstant(object):
  def __init__(self, id, expression, _fcrd):
    self.id = id
    self.expression = expression
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'expression', 'id'], self, state)
class TransformCompare(object):
  def __init__(self, id, _fcrd):
    self.id = id
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'id'], self, state)
class TransformDefinition(object):
  def __init__(self, compares, locals, expression, _fcrd):
    self.compares = compares
    self.locals = locals
    self.expression = expression
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'compares', 'expression', 'locals'], self, state)
_id = str
Id = _id
ImportDomainW = ImportDomain
ImportDomainAs = Id
RealmDomainDeclaration = DomainDeclaration
DomainDeclarationId = _id
InnerDomainDeclaration = DomainDeclaration
ExpressionLiteralString = str
ExpressionArguments = list
ExpressionLookup = Expression
Codomain = Expression
VariableDeclaration = VariableDefinition
VariableConstraintsArgument = Expression
VariableDomain = Expression
# Main parser
class _ParserImpl(object):
  on_realm_path = 0
  on_realm_domain_import = 1
  on_domain_declaration_id = 2
  def __init__(self, reader, interceptor):
    self._reader = reader
    self.interceptor = interceptor
  def __call__(self):
    return self._parse_realm()
  def _parse_realm(self):
    value = self._reader.parse_type(
      result_type=Realm,
      error='expected realm',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseValue(value=self._reader.get_coord(), coord=self._reader.get_coord())),
        ('imports', 'expected realm-domain-import in realm', lambda: self._reader.parse_many_wp(self._parse_realm_domain_import, 0, 9223372036854775807)),
        ('domains', 'expected realm-domain-declaration in realm', lambda: self._reader.parse_many_wp(self._parse_realm_domain_declaration, 0, 9223372036854775807)),
        ('', 'expected w in realm', self._parse_w),
        ('', 'expected eof', self._reader.consume_eof),
      ])
    return value
  def _parse_ws(self, imin=1, imax=1):
    value = self._reader.parse_type(
      result_type=Ws,
      error='expected ws',
      parsers=[
        ('_fimm', 'expected ws', lambda: self._reader.consume_string(SimpleClassPredicate(' \n'), imin, imax))
      ],
      result_immediate='_fimm')
    return value
  def _parse_pseudo_letter(self, imin=1, imax=1):
    value = self._reader.parse_type(
      result_type=PseudoLetter,
      error='expected pseudo-letter',
      parsers=[
        ('_fimm', 'expected pseudo-letter', lambda: self._reader.consume_string(SimpleClassPredicate("a-zA-Z_'"), imin, imax))
      ],
      result_immediate='_fimm')
    return value
  def _parse_dot(self):
    value = self._reader.parse_type(
      result_type=Dot,
      error='expected dot',
      parsers=[
        ('_fimm', 'expected dot', lambda: self._reader.consume_string(StringPredicate('.'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_domain_literal_full(self):
    value = self._reader.parse_type(
      result_type=DomainLiteralFull,
      error='expected domain-literal-full',
      parsers=[
        ('_fimm', 'expected domain-literal-full', lambda: self._reader.consume_string(StringPredicate('domain'), 6, 6))
      ],
      result_immediate='_fimm')
    return value
  def _parse_domain_literal_min(self):
    value = self._reader.parse_type(
      result_type=DomainLiteralMin,
      error='expected domain-literal-min',
      parsers=[
        ('_fimm', 'expected domain-literal-min', lambda: self._reader.consume_string(StringPredicate('d'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_from(self):
    value = self._reader.parse_type(
      result_type=From,
      error='expected from',
      parsers=[
        ('_fimm', 'expected from', lambda: self._reader.consume_string(StringPredicate('from'), 4, 4))
      ],
      result_immediate='_fimm')
    return value
  def _parse_import_literal_full(self):
    value = self._reader.parse_type(
      result_type=ImportLiteralFull,
      error='expected import-literal-full',
      parsers=[
        ('_fimm', 'expected import-literal-full', lambda: self._reader.consume_string(StringPredicate('import'), 6, 6))
      ],
      result_immediate='_fimm')
    return value
  def _parse_import_literal_min(self):
    value = self._reader.parse_type(
      result_type=ImportLiteralMin,
      error='expected import-literal-min',
      parsers=[
        ('_fimm', 'expected import-literal-min', lambda: self._reader.consume_string(StringPredicate('i'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_as(self):
    value = self._reader.parse_type(
      result_type=As,
      error='expected as',
      parsers=[
        ('_fimm', 'expected as', lambda: self._reader.consume_string(StringPredicate('as'), 2, 2))
      ],
      result_immediate='_fimm')
    return value
  def _parse_left_curly_bracket(self):
    value = self._reader.parse_type(
      result_type=LeftCurlyBracket,
      error='expected left-curly-bracket',
      parsers=[
        ('_fimm', 'expected left-curly-bracket', lambda: self._reader.consume_string(StringPredicate('{'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_right_curly_bracket(self):
    value = self._reader.parse_type(
      result_type=RightCurlyBracket,
      error='expected right-curly-bracket',
      parsers=[
        ('_fimm', 'expected right-curly-bracket', lambda: self._reader.consume_string(StringPredicate('}'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_left_square_bracket(self):
    value = self._reader.parse_type(
      result_type=LeftSquareBracket,
      error='expected left-square-bracket',
      parsers=[
        ('_fimm', 'expected left-square-bracket', lambda: self._reader.consume_string(StringPredicate('['), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_right_square_bracket(self):
    value = self._reader.parse_type(
      result_type=RightSquareBracket,
      error='expected right-square-bracket',
      parsers=[
        ('_fimm', 'expected right-square-bracket', lambda: self._reader.consume_string(StringPredicate(']'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_vertical_line(self):
    value = self._reader.parse_type(
      result_type=VerticalLine,
      error='expected vertical-line',
      parsers=[
        ('_fimm', 'expected vertical-line', lambda: self._reader.consume_string(StringPredicate('|'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_colon(self):
    value = self._reader.parse_type(
      result_type=Colon,
      error='expected colon',
      parsers=[
        ('_fimm', 'expected colon', lambda: self._reader.consume_string(StringPredicate(':'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_double_colon(self):
    value = self._reader.parse_type(
      result_type=DoubleColon,
      error='expected double-colon',
      parsers=[
        ('_fimm', 'expected double-colon', lambda: self._reader.consume_string(StringPredicate('::'), 2, 2))
      ],
      result_immediate='_fimm')
    return value
  def _parse_greater_than_sign(self):
    value = self._reader.parse_type(
      result_type=GreaterThanSign,
      error='expected greater-than-sign',
      parsers=[
        ('_fimm', 'expected greater-than-sign', lambda: self._reader.consume_string(StringPredicate('>'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_equals_sign(self):
    value = self._reader.parse_type(
      result_type=EqualsSign,
      error='expected equals-sign',
      parsers=[
        ('_fimm', 'expected equals-sign', lambda: self._reader.consume_string(StringPredicate('='), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_dollar_sign(self):
    value = self._reader.parse_type(
      result_type=DollarSign,
      error='expected dollar-sign',
      parsers=[
        ('_fimm', 'expected dollar-sign', lambda: self._reader.consume_string(StringPredicate('$'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_ampersand(self):
    value = self._reader.parse_type(
      result_type=Ampersand,
      error='expected ampersand',
      parsers=[
        ('_fimm', 'expected ampersand', lambda: self._reader.consume_string(StringPredicate('&'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_left_parenthesis(self):
    value = self._reader.parse_type(
      result_type=LeftParenthesis,
      error='expected left-parenthesis',
      parsers=[
        ('_fimm', 'expected left-parenthesis', lambda: self._reader.consume_string(StringPredicate('('), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_right_parenthesis(self):
    value = self._reader.parse_type(
      result_type=RightParenthesis,
      error='expected right-parenthesis',
      parsers=[
        ('_fimm', 'expected right-parenthesis', lambda: self._reader.consume_string(StringPredicate(')'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_tilde(self):
    value = self._reader.parse_type(
      result_type=Tilde,
      error='expected tilde',
      parsers=[
        ('_fimm', 'expected tilde', lambda: self._reader.consume_string(StringPredicate('~'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_solidus(self):
    value = self._reader.parse_type(
      result_type=Solidus,
      error='expected solidus',
      parsers=[
        ('_fimm', 'expected solidus', lambda: self._reader.consume_string(StringPredicate('/'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_percent_sign(self):
    value = self._reader.parse_type(
      result_type=PercentSign,
      error='expected percent-sign',
      parsers=[
        ('_fimm', 'expected percent-sign', lambda: self._reader.consume_string(StringPredicate('%'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_octothorp(self):
    value = self._reader.parse_type(
      result_type=Octothorp,
      error='expected octothorp',
      parsers=[
        ('_fimm', 'expected octothorp', lambda: self._reader.consume_string(StringPredicate('#'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_line_feed(self):
    value = self._reader.parse_type(
      result_type=LineFeed,
      error='expected line-feed',
      parsers=[
        ('_fimm', 'expected line-feed', lambda: self._reader.consume_string(StringPredicate('\n'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_line_comment_content(self, imin=1, imax=1):
    value = self._reader.parse_type(
      result_type=LineCommentContent,
      error='expected line-comment-content',
      parsers=[
        ('_fimm', 'expected line-comment-content', lambda: self._reader.consume_string(SimpleClassPredicate('^\n'), imin, imax))
      ],
      result_immediate='_fimm')
    return value
  def _parse_left_to_right_arrow(self):
    value = self._reader.parse_type(
      result_type=LeftToRightArrow,
      error='expected left-to-right-arrow',
      parsers=[
        ('_fimm', 'expected left-to-right-arrow', lambda: self._reader.consume_string(StringPredicate('->'), 2, 2))
      ],
      result_immediate='_fimm')
    return value
  def _parse_single_quote(self):
    value = self._reader.parse_type(
      result_type=SingleQuote,
      error='expected single-quote',
      parsers=[
        ('_fimm', 'expected single-quote', lambda: self._reader.consume_string(StringPredicate("'"), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_double_quote(self):
    value = self._reader.parse_type(
      result_type=DoubleQuote,
      error='expected double-quote',
      parsers=[
        ('_fimm', 'expected double-quote', lambda: self._reader.consume_string(StringPredicate('"'), 1, 1))
      ],
      result_immediate='_fimm')
    return value
  def _parse_domain(self):
    value = self._reader.parse_type(
      result_type=Domain,
      error='expected domain',
      parsers=[
        ('_fimm', 'expected domain, any of domain-literal-full, domain-literal-min', lambda: self._reader.parse_any([self._parse_domain_literal_full,self._parse_domain_literal_min]))
      ],
      result_immediate='_fimm')
    return value
  def _parse_import(self):
    value = self._reader.parse_type(
      result_type=Import,
      error='expected import',
      parsers=[
        ('_fimm', 'expected import, any of import-literal-full, import-literal-min', lambda: self._reader.parse_any([self._parse_import_literal_full,self._parse_import_literal_min]))
      ],
      result_immediate='_fimm')
    return value
  def _parse_ww(self):
    value = self._reader.parse_type(
      result_type=Ww,
      error='expected ww',
      parsers=[
        ('', 'expected ws in ww', lambda: self._parse_ws(0, 9223372036854775807)),
        ('', 'expected line-comment in ww', lambda: self._reader.parse_many_wp(self._parse_line_comment, 0, 1)),
      ])
    return value
  def _parse_w(self):
    value = self._reader.parse_type(
      result_type=W,
      error='expected w',
      parsers=[
        ('', 'expected ww in w', lambda: self._reader.parse_many_wp(self._parse_ww, 0, 9223372036854775807)),
      ])
    return value
  def _parse_line_comment(self):
    value = self._reader.parse_type(
      result_type=LineComment,
      error='expected line-comment',
      parsers=[
        ('', 'expected octothorp in line-comment', self._parse_octothorp),
        ('', 'expected line-comment-content in line-comment', lambda: self._parse_line_comment_content(0, 9223372036854775807)),
        ('', 'expected line-feed in line-comment', lambda: self._reader.parse_many_wp(self._parse_line_feed, 0, 1)),
      ])
    return value
  def _parse__id(self):
    value = self._reader.parse_type(
      result_type=_id,
      error='expected _id',
      parsers=[
        ('_fimm', 'expected pseudo-letter in _id', lambda: self._parse_pseudo_letter(1, 9223372036854775807)),
      ],
      result_immediate='_fimm')
    return value
  def _parse_id(self):
    value = self._reader.parse_type(
      result_type=Id,
      error='expected id',
      parsers=[
        ('', 'expected w in id', self._parse_w),
        ('_fimm', 'expected _id in id', self._parse__id),
      ],
      result_immediate='_fimm')
    return value
  def _parse_variable_prefix(self):
    value = self._reader.parse_type(
      result_type=VariablePrefix,
      error='expected variable-prefix',
      parsers=[
        ('', 'expected w in variable-prefix', self._parse_w),
        ('', 'expected dot in variable-prefix', self._parse_dot),
      ])
    return value
  def _parse_realm_path(self):
    value = self._reader.parse_type(
      result_type=RealmPath,
      error='expected realm-path',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseValue(value=self._reader.get_coord(), coord=self._reader.get_coord())),
        ('', 'expected w in realm-path', self._parse_w),
        ('local', 'expected dot in realm-path', lambda: self._reader.parse_many_wp(self._parse_dot, 0, 1)),
        ('path', 'expected realm-path-branch in realm-path', lambda: self._reader.parse_many_wp(self._parse_realm_path_branch, 1, 9223372036854775807)),
      ])
    value = self.interceptor.trigger(self.on_realm_path, value)
    return value
  def _parse_realm_path_branch(self):
    value = self._reader.parse_type(
      result_type=RealmPathBranch,
      error='expected realm-path-branch',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseValue(value=self._reader.get_coord(), coord=self._reader.get_coord())),
        ('', 'expected solidus in realm-path-branch', self._parse_solidus),
        ('realm', 'expected id in realm-path-branch', self._parse_id),
      ])
    return value
  def _parse_realm_domain_import(self):
    value = self._reader.parse_type(
      result_type=RealmDomainImport,
      error='expected realm-domain-import',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseValue(value=self._reader.get_coord(), coord=self._reader.get_coord())),
        ('', 'expected w in realm-domain-import', self._parse_w),
        ('', 'expected from in realm-domain-import', self._parse_from),
        ('realm', 'expected realm-path in realm-domain-import', self._parse_realm_path),
        ('', 'expected w in realm-domain-import', self._parse_w),
        ('', 'expected left-curly-bracket in realm-domain-import', self._parse_left_curly_bracket),
        ('domains', 'expected import-domain-w in realm-domain-import', lambda: self._reader.parse_many_wp(self._parse_import_domain_w, 1, 9223372036854775807)),
        ('', 'expected w in realm-domain-import', self._parse_w),
        ('', 'expected right-curly-bracket in realm-domain-import', self._parse_right_curly_bracket),
      ])
    value = self.interceptor.trigger(self.on_realm_domain_import, value)
    return value
  def _parse_import_domain(self):
    value = self._reader.parse_type(
      result_type=ImportDomain,
      error='expected import-domain',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseValue(value=self._reader.get_coord(), coord=self._reader.get_coord())),
        ('', 'expected import in import-domain', self._parse_import),
        ('domain', 'expected id in import-domain', self._parse_id),
        ('as_domain', 'expected import-domain-as in import-domain', lambda: self._reader.parse_many_wp(self._parse_import_domain_as, 0, 1)),
      ])
    return value
  def _parse_import_domain_w(self):
    value = self._reader.parse_type(
      result_type=ImportDomainW,
      error='expected import-domain-w',
      parsers=[
        ('', 'expected w in import-domain-w', self._parse_w),
        ('_fimm', 'expected import-domain in import-domain-w', self._parse_import_domain),
      ],
      result_immediate='_fimm')
    return value
  def _parse_import_domain_as(self):
    value = self._reader.parse_type(
      result_type=ImportDomainAs,
      error='expected import-domain-as',
      parsers=[
        ('', 'expected w in import-domain-as', self._parse_w),
        ('', 'expected as in import-domain-as', self._parse_as),
        ('_fimm', 'expected id in import-domain-as', self._parse_id),
      ],
      result_immediate='_fimm')
    return value
  def _parse_domain_declaration(self):
    value = self._reader.parse_type(
      result_type=DomainDeclaration,
      error='expected domain-declaration',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseValue(value=self._reader.get_coord(), coord=self._reader.get_coord())),
        ('id', 'expected domain-declaration-id in domain-declaration', self._parse_domain_declaration_id),
        ('codomain', 'expected codomain in domain-declaration', lambda: self._reader.parse_many_wp(self._parse_codomain, 0, 1)),
        ('domain', 'expected domain-definition in domain-declaration', lambda: self._reader.parse_many_wp(self._parse_domain_definition, 0, 1)),
      ])
    return value
  def _parse_realm_domain_declaration(self):
    value = self._reader.parse_type(
      result_type=RealmDomainDeclaration,
      error='expected realm-domain-declaration',
      parsers=[
        ('', 'expected w in realm-domain-declaration', self._parse_w),
        ('', 'expected domain in realm-domain-declaration', self._parse_domain),
        ('', 'expected w in realm-domain-declaration', self._parse_w),
        ('_fimm', 'expected domain-declaration in realm-domain-declaration', self._parse_domain_declaration),
      ],
      result_immediate='_fimm')
    return value
  def _parse_domain_declaration_id(self):
    value = self._reader.parse_type(
      result_type=DomainDeclarationId,
      error='expected domain-declaration-id',
      parsers=[
        ('_fimm', 'expected _id in domain-declaration-id', self._parse__id),
      ],
      result_immediate='_fimm')
    value = self.interceptor.trigger(self.on_domain_declaration_id, value)
    return value
  def _parse_domain_definition(self):
    value = self._reader.parse_type(
      result_type=DomainDefinition,
      error='expected domain-definition',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseValue(value=self._reader.get_coord(), coord=self._reader.get_coord())),
        ('', 'expected w in domain-definition', self._parse_w),
        ('', 'expected left-curly-bracket in domain-definition', self._parse_left_curly_bracket),
        ('variables', 'expected variable-declaration in domain-definition', lambda: self._reader.parse_many_wp(self._parse_variable_declaration, 0, 9223372036854775807)),
        ('domains', 'expected inner-domain-declaration in domain-definition', lambda: self._reader.parse_many_wp(self._parse_inner_domain_declaration, 0, 9223372036854775807)),
        ('transforms', 'expected transform-definition in domain-definition', lambda: self._reader.parse_many_wp(self._parse_transform_definition, 0, 9223372036854775807)),
        ('', 'expected w in domain-definition', self._parse_w),
        ('', 'expected right-curly-bracket in domain-definition', self._parse_right_curly_bracket),
      ])
    return value
  def _parse_inner_domain_declaration(self):
    value = self._reader.parse_type(
      result_type=InnerDomainDeclaration,
      error='expected inner-domain-declaration',
      parsers=[
        ('', 'expected w in inner-domain-declaration', self._parse_w),
        ('', 'expected vertical-line in inner-domain-declaration', self._parse_vertical_line),
        ('', 'expected w in inner-domain-declaration', self._parse_w),
        ('_fimm', 'expected domain-declaration in inner-domain-declaration', self._parse_domain_declaration),
      ],
      result_immediate='_fimm')
    return value
  def _parse_expression(self):
    value = self._reader.parse_type(
      result_type=Expression,
      error='expected expression',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseValue(value=self._reader.get_coord(), coord=self._reader.get_coord())),
        ('', 'expected w in expression', self._parse_w),
        ('alt', 'expected expression-alt in expression', self._parse_expression_alt),
      ])
    return value
  def _parse_expression_alt(self):
    value = self._reader.parse_type(
      result_type=ExpressionAlt,
      error='expected expression-alt',
      parsers=[
        ('_fimm', 'expected expression-alt, any of expression-literal, expression-domain', lambda: self._reader.parse_any([self._parse_expression_literal,self._parse_expression_domain]))
      ],
      result_immediate='_fimm')
    return value
  def _parse_expression_domain(self):
    value = self._reader.parse_type(
      result_type=ExpressionDomain,
      error='expected expression-domain',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseValue(value=self._reader.get_coord(), coord=self._reader.get_coord())),
        ('domainof', 'expected ampersand in expression-domain', lambda: self._reader.parse_many_wp(self._parse_ampersand, 0, 1)),
        ('id', 'expected id in expression-domain', self._parse_id),
        ('arguments', 'expected expression-arguments in expression-domain', lambda: self._reader.parse_many_wp(self._parse_expression_arguments, 0, 1)),
        ('lookup', 'expected expression-lookup in expression-domain', lambda: self._reader.parse_many_wp(self._parse_expression_lookup, 0, 1)),
      ])
    return value
  def _parse_expression_literal(self):
    value = self._reader.parse_type(
      result_type=ExpressionLiteral,
      error='expected expression-literal',
      parsers=[
        ('_fimm', 'expected expression-literal, any of expression-literal-string', lambda: self._reader.parse_any([self._parse_expression_literal_string]))
      ],
      result_immediate='_fimm')
    return value
  def _parse_expression_literal_string_content(self, imin=1, imax=1):
    value = self._reader.parse_type(
      result_type=ExpressionLiteralStringContent,
      error='expected expression-literal-string-content',
      parsers=[
        ('_fimm', 'expected expression-literal-string-content', lambda: self._reader.consume_string(FixedEscapedClassPredicate("^'", '\\\\'), imin, imax))
      ],
      result_immediate='_fimm')
    return value
  def _parse_expression_literal_string(self):
    value = self._reader.parse_type(
      result_type=ExpressionLiteralString,
      error='expected expression-literal-string',
      parsers=[
        ('', 'expected single-quote in expression-literal-string', self._parse_single_quote),
        ('_fimm', 'expected expression-literal-string-content in expression-literal-string', lambda: self._parse_expression_literal_string_content(0, 9223372036854775807)),
        ('', 'expected single-quote in expression-literal-string', self._parse_single_quote),
      ],
      result_immediate='_fimm')
    return value
  def _parse_expression_argument(self):
    value = self._reader.parse_type(
      result_type=ExpressionArgument,
      error='expected expression-argument',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseValue(value=self._reader.get_coord(), coord=self._reader.get_coord())),
        ('', 'expected variable-prefix in expression-argument', self._parse_variable_prefix),
        ('id', 'expected id in expression-argument', self._parse_id),
        ('', 'expected w in expression-argument', self._parse_w),
        ('', 'expected tilde in expression-argument', self._parse_tilde),
        ('expression', 'expected expression in expression-argument', self._parse_expression),
      ])
    return value
  def _parse_expression_arguments(self):
    value = self._reader.parse_type(
      result_type=ExpressionArguments,
      error='expected expression-arguments',
      parsers=[
        ('', 'expected w in expression-arguments', self._parse_w),
        ('', 'expected left-parenthesis in expression-arguments', self._parse_left_parenthesis),
        ('_fimm', 'expected expression-argument in expression-arguments', lambda: self._reader.parse_many_wp(self._parse_expression_argument, 0, 9223372036854775807)),
        ('', 'expected w in expression-arguments', self._parse_w),
        ('', 'expected right-parenthesis in expression-arguments', self._parse_right_parenthesis),
      ],
      result_immediate='_fimm')
    return value
  def _parse_expression_lookup(self):
    value = self._reader.parse_type(
      result_type=ExpressionLookup,
      error='expected expression-lookup',
      parsers=[
        ('', 'expected w in expression-lookup', self._parse_w),
        ('', 'expected solidus in expression-lookup', self._parse_solidus),
        ('_fimm', 'expected expression in expression-lookup', self._parse_expression),
      ],
      result_immediate='_fimm')
    return value
  def _parse_codomain(self):
    value = self._reader.parse_type(
      result_type=Codomain,
      error='expected codomain',
      parsers=[
        ('', 'expected w in codomain', self._parse_w),
        ('', 'expected left-to-right-arrow in codomain', self._parse_left_to_right_arrow),
        ('', 'expected w in codomain', self._parse_w),
        ('_fimm', 'expected expression in codomain', self._parse_expression),
      ],
      result_immediate='_fimm')
    return value
  def _parse_variable_definition(self):
    value = self._reader.parse_type(
      result_type=VariableDefinition,
      error='expected variable-definition',
      parsers=[
        ('_fimm', 'expected variable-definition, any of variable-constant, variable-bound', lambda: self._reader.parse_any([self._parse_variable_constant,self._parse_variable_bound]))
      ],
      result_immediate='_fimm')
    return value
  def _parse_variable_declaration(self):
    value = self._reader.parse_type(
      result_type=VariableDeclaration,
      error='expected variable-declaration',
      parsers=[
        ('', 'expected variable-prefix in variable-declaration', self._parse_variable_prefix),
        ('', 'expected w in variable-declaration', self._parse_w),
        ('_fimm', 'expected variable-definition in variable-declaration', self._parse_variable_definition),
      ],
      result_immediate='_fimm')
    return value
  def _parse_variable_constraints_argument(self):
    value = self._reader.parse_type(
      result_type=VariableConstraintsArgument,
      error='expected variable-constraints-argument',
      parsers=[
        ('', 'expected variable-prefix in variable-constraints-argument', self._parse_variable_prefix),
        ('_fimm', 'expected expression in variable-constraints-argument', self._parse_expression),
      ],
      result_immediate='_fimm')
    return value
  def _parse_variable_constraints(self):
    value = self._reader.parse_type(
      result_type=VariableConstraints,
      error='expected variable-constraints',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseValue(value=self._reader.get_coord(), coord=self._reader.get_coord())),
        ('', 'expected w in variable-constraints', self._parse_w),
        ('', 'expected double-colon in variable-constraints', self._parse_double_colon),
        ('', 'expected w in variable-constraints', self._parse_w),
        ('', 'expected left-square-bracket in variable-constraints', self._parse_left_square_bracket),
        ('constraints', 'expected variable-constraints-argument in variable-constraints', lambda: self._reader.parse_many_wp(self._parse_variable_constraints_argument, 1, 9223372036854775807)),
        ('', 'expected right-square-bracket in variable-constraints', self._parse_right_square_bracket),
      ])
    return value
  def _parse_variable_domain(self):
    value = self._reader.parse_type(
      result_type=VariableDomain,
      error='expected variable-domain',
      parsers=[
        ('', 'expected w in variable-domain', self._parse_w),
        ('', 'expected colon in variable-domain', self._parse_colon),
        ('_fimm', 'expected expression in variable-domain', self._parse_expression),
      ],
      result_immediate='_fimm')
    return value
  def _parse_variable_bound(self):
    value = self._reader.parse_type(
      result_type=VariableBound,
      error='expected variable-bound',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseValue(value=self._reader.get_coord(), coord=self._reader.get_coord())),
        ('id', 'expected _id in variable-bound', self._parse__id),
        ('variable_domain', 'expected variable-domain in variable-bound', lambda: self._reader.parse_many_wp(self._parse_variable_domain, 0, 1)),
        ('variable_constraints', 'expected variable-constraints in variable-bound', lambda: self._reader.parse_many_wp(self._parse_variable_constraints, 0, 1)),
      ])
    return value
  def _parse_variable_constant(self):
    value = self._reader.parse_type(
      result_type=VariableConstant,
      error='expected variable-constant',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseValue(value=self._reader.get_coord(), coord=self._reader.get_coord())),
        ('id', 'expected _id in variable-constant', self._parse__id),
        ('', 'expected w in variable-constant', self._parse_w),
        ('', 'expected tilde in variable-constant', self._parse_tilde),
        ('expression', 'expected expression in variable-constant', self._parse_expression),
      ])
    return value
  def _parse_transform_compare(self):
    value = self._reader.parse_type(
      result_type=TransformCompare,
      error='expected transform-compare',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseValue(value=self._reader.get_coord(), coord=self._reader.get_coord())),
        ('', 'expected variable-prefix in transform-compare', self._parse_variable_prefix),
        ('id', 'expected id in transform-compare', self._parse_id),
        ('', 'expected w in transform-compare', self._parse_w),
        ('', 'expected equals-sign in transform-compare', self._parse_equals_sign),
        ('id', 'expected id in transform-compare', self._parse_id),
      ])
    return value
  def _parse_transform_definition(self):
    value = self._reader.parse_type(
      result_type=TransformDefinition,
      error='expected transform-definition',
      parsers=[
        ('_fcrd', 'built-in coord record', lambda: ParseValue(value=self._reader.get_coord(), coord=self._reader.get_coord())),
        ('', 'expected w in transform-definition', self._parse_w),
        ('', 'expected greater-than-sign in transform-definition', self._parse_greater_than_sign),
        ('compares', 'expected transform-compare in transform-definition', lambda: self._reader.parse_many_wp(self._parse_transform_compare, 0, 9223372036854775807)),
        ('', 'expected w in transform-definition', self._parse_w),
        ('', 'expected dollar-sign in transform-definition', self._parse_dollar_sign),
        ('locals', 'expected expression-argument in transform-definition', lambda: self._reader.parse_many_wp(self._parse_expression_argument, 0, 9223372036854775807)),
        ('expression', 'expected expression in transform-definition', self._parse_expression),
      ])
    return value
Parser = _ParserImpl
