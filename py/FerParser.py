# AUTOMATICLY GENERATED FILE.
# ALL CHANGES TO THIS FILE WILL BE DISCARDED.
# Updated on 2017-08-04 18:37:15.410538
import datetime
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
PseudoNumber = str
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
Hyphen = str
Domain = idem
Import = idem
Ww = str
W_old = str
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
  def __init__(self, value, _fcrd):
    self.value = value
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'value'], self, state)
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
class ExpressionLiteralIntegerDecimal(object):
  def __init__(self, minus, ipart, _fcrd):
    self.minus = minus
    self.ipart = ipart
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'ipart', 'minus'], self, state)
class ExpressionLiteralFloat(object):
  def __init__(self, minus, ipart, dpart, _fcrd):
    self.minus = minus
    self.ipart = ipart
    self.dpart = dpart
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'dpart', 'ipart', 'minus'], self, state)
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
  def __init__(self, variable, domain, _fcrd):
    self.variable = variable
    self.domain = domain
    self._fcrd = _fcrd
  def __pformat__(self, state):
    pformat_class(['_fcrd', 'domain', 'variable'], self, state)
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
  on_integer_decimal = 3
  on_float = 4
  def __init__(self, reader, interceptor):
    self._reader = reader
    self.interceptor = interceptor
  def __call__(self):
    return self._parse_realm()
  def _parse_realm(self):
    begin_time = datetime.datetime.now()
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: Realm(_fcrd=coord, **kwargs),
      error='expected realm',
      parsers=[
        ('imports', 'expected realm-domain-import (as imports) in realm', lambda: self._reader.parse_many_wp(self._parse_realm_domain_import, 0, 9223372036854775807)),
        ('domains', 'expected realm-domain-declaration (as domains) in realm', lambda: self._reader.parse_many_wp(self._parse_realm_domain_declaration, 0, 9223372036854775807)),
        ('', 'expected w in realm', self._parse_w),
        ('', 'expected eof', self._reader.consume_eof),
      ]
      )
    end_time = datetime.datetime.now()
    self._reader.stats['meta']['time'] = str(end_time-begin_time)
    return value
  _ws_predicate = SimpleClassPredicate.factory(r' \n')
  def _parse_ws(self, imin=1, imax=1):
    value = self._reader.parse_type(
      result_type=Ws,
      error='expected ws',
      parsers=[
        ('_fimm', 'expected ws', lambda: self._reader.consume_string(self._ws_predicate, imin, imax))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _pseudo_letter_predicate = SimpleClassPredicate.factory(r"a-zA-Z_'")
  def _parse_pseudo_letter(self, imin=1, imax=1):
    value = self._reader.parse_type(
      result_type=PseudoLetter,
      error='expected pseudo-letter',
      parsers=[
        ('_fimm', 'expected pseudo-letter', lambda: self._reader.consume_string(self._pseudo_letter_predicate, imin, imax))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _pseudo_number_predicate = SimpleClassPredicate.factory(r'0-9')
  def _parse_pseudo_number(self, imin=1, imax=1):
    value = self._reader.parse_type(
      result_type=PseudoNumber,
      error='expected pseudo-number',
      parsers=[
        ('_fimm', 'expected pseudo-number', lambda: self._reader.consume_string(self._pseudo_number_predicate, imin, imax))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _dot_predicate = StringPredicate(r'.')
  def _parse_dot(self):
    value = self._reader.parse_type(
      result_type=Dot,
      error='expected dot',
      parsers=[
        ('_fimm', 'expected dot', lambda: self._reader.consume_string(self._dot_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _domain_literal_full_predicate = StringPredicate(r'domain')
  def _parse_domain_literal_full(self):
    value = self._reader.parse_type(
      result_type=DomainLiteralFull,
      error='expected domain-literal-full',
      parsers=[
        ('_fimm', 'expected domain-literal-full', lambda: self._reader.consume_string(self._domain_literal_full_predicate, 6, 6))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _domain_literal_min_predicate = StringPredicate(r'd')
  def _parse_domain_literal_min(self):
    value = self._reader.parse_type(
      result_type=DomainLiteralMin,
      error='expected domain-literal-min',
      parsers=[
        ('_fimm', 'expected domain-literal-min', lambda: self._reader.consume_string(self._domain_literal_min_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _from_predicate = StringPredicate(r'from')
  def _parse_from(self):
    value = self._reader.parse_type(
      result_type=From,
      error='expected from',
      parsers=[
        ('_fimm', 'expected from', lambda: self._reader.consume_string(self._from_predicate, 4, 4))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _import_literal_full_predicate = StringPredicate(r'import')
  def _parse_import_literal_full(self):
    value = self._reader.parse_type(
      result_type=ImportLiteralFull,
      error='expected import-literal-full',
      parsers=[
        ('_fimm', 'expected import-literal-full', lambda: self._reader.consume_string(self._import_literal_full_predicate, 6, 6))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _import_literal_min_predicate = StringPredicate(r'i')
  def _parse_import_literal_min(self):
    value = self._reader.parse_type(
      result_type=ImportLiteralMin,
      error='expected import-literal-min',
      parsers=[
        ('_fimm', 'expected import-literal-min', lambda: self._reader.consume_string(self._import_literal_min_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _as_predicate = StringPredicate(r'as')
  def _parse_as(self):
    value = self._reader.parse_type(
      result_type=As,
      error='expected as',
      parsers=[
        ('_fimm', 'expected as', lambda: self._reader.consume_string(self._as_predicate, 2, 2))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _left_curly_bracket_predicate = StringPredicate(r'{')
  def _parse_left_curly_bracket(self):
    value = self._reader.parse_type(
      result_type=LeftCurlyBracket,
      error='expected left-curly-bracket',
      parsers=[
        ('_fimm', 'expected left-curly-bracket', lambda: self._reader.consume_string(self._left_curly_bracket_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _right_curly_bracket_predicate = StringPredicate(r'}')
  def _parse_right_curly_bracket(self):
    value = self._reader.parse_type(
      result_type=RightCurlyBracket,
      error='expected right-curly-bracket',
      parsers=[
        ('_fimm', 'expected right-curly-bracket', lambda: self._reader.consume_string(self._right_curly_bracket_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _left_square_bracket_predicate = StringPredicate(r'[')
  def _parse_left_square_bracket(self):
    value = self._reader.parse_type(
      result_type=LeftSquareBracket,
      error='expected left-square-bracket',
      parsers=[
        ('_fimm', 'expected left-square-bracket', lambda: self._reader.consume_string(self._left_square_bracket_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _right_square_bracket_predicate = StringPredicate(r']')
  def _parse_right_square_bracket(self):
    value = self._reader.parse_type(
      result_type=RightSquareBracket,
      error='expected right-square-bracket',
      parsers=[
        ('_fimm', 'expected right-square-bracket', lambda: self._reader.consume_string(self._right_square_bracket_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _vertical_line_predicate = StringPredicate(r'|')
  def _parse_vertical_line(self):
    value = self._reader.parse_type(
      result_type=VerticalLine,
      error='expected vertical-line',
      parsers=[
        ('_fimm', 'expected vertical-line', lambda: self._reader.consume_string(self._vertical_line_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _colon_predicate = StringPredicate(r':')
  def _parse_colon(self):
    value = self._reader.parse_type(
      result_type=Colon,
      error='expected colon',
      parsers=[
        ('_fimm', 'expected colon', lambda: self._reader.consume_string(self._colon_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _double_colon_predicate = StringPredicate(r'::')
  def _parse_double_colon(self):
    value = self._reader.parse_type(
      result_type=DoubleColon,
      error='expected double-colon',
      parsers=[
        ('_fimm', 'expected double-colon', lambda: self._reader.consume_string(self._double_colon_predicate, 2, 2))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _greater_than_sign_predicate = StringPredicate(r'>')
  def _parse_greater_than_sign(self):
    value = self._reader.parse_type(
      result_type=GreaterThanSign,
      error='expected greater-than-sign',
      parsers=[
        ('_fimm', 'expected greater-than-sign', lambda: self._reader.consume_string(self._greater_than_sign_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _equals_sign_predicate = StringPredicate(r'=')
  def _parse_equals_sign(self):
    value = self._reader.parse_type(
      result_type=EqualsSign,
      error='expected equals-sign',
      parsers=[
        ('_fimm', 'expected equals-sign', lambda: self._reader.consume_string(self._equals_sign_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _dollar_sign_predicate = StringPredicate(r'$')
  def _parse_dollar_sign(self):
    value = self._reader.parse_type(
      result_type=DollarSign,
      error='expected dollar-sign',
      parsers=[
        ('_fimm', 'expected dollar-sign', lambda: self._reader.consume_string(self._dollar_sign_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _ampersand_predicate = StringPredicate(r'&')
  def _parse_ampersand(self):
    value = self._reader.parse_type(
      result_type=Ampersand,
      error='expected ampersand',
      parsers=[
        ('_fimm', 'expected ampersand', lambda: self._reader.consume_string(self._ampersand_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _left_parenthesis_predicate = StringPredicate(r'(')
  def _parse_left_parenthesis(self):
    value = self._reader.parse_type(
      result_type=LeftParenthesis,
      error='expected left-parenthesis',
      parsers=[
        ('_fimm', 'expected left-parenthesis', lambda: self._reader.consume_string(self._left_parenthesis_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _right_parenthesis_predicate = StringPredicate(r')')
  def _parse_right_parenthesis(self):
    value = self._reader.parse_type(
      result_type=RightParenthesis,
      error='expected right-parenthesis',
      parsers=[
        ('_fimm', 'expected right-parenthesis', lambda: self._reader.consume_string(self._right_parenthesis_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _tilde_predicate = StringPredicate(r'~')
  def _parse_tilde(self):
    value = self._reader.parse_type(
      result_type=Tilde,
      error='expected tilde',
      parsers=[
        ('_fimm', 'expected tilde', lambda: self._reader.consume_string(self._tilde_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _solidus_predicate = StringPredicate(r'/')
  def _parse_solidus(self):
    value = self._reader.parse_type(
      result_type=Solidus,
      error='expected solidus',
      parsers=[
        ('_fimm', 'expected solidus', lambda: self._reader.consume_string(self._solidus_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _percent_sign_predicate = StringPredicate(r'%')
  def _parse_percent_sign(self):
    value = self._reader.parse_type(
      result_type=PercentSign,
      error='expected percent-sign',
      parsers=[
        ('_fimm', 'expected percent-sign', lambda: self._reader.consume_string(self._percent_sign_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _octothorp_predicate = StringPredicate(r'#')
  def _parse_octothorp(self):
    value = self._reader.parse_type(
      result_type=Octothorp,
      error='expected octothorp',
      parsers=[
        ('_fimm', 'expected octothorp', lambda: self._reader.consume_string(self._octothorp_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _line_feed_predicate = StringPredicate(r'\n')
  def _parse_line_feed(self):
    value = self._reader.parse_type(
      result_type=LineFeed,
      error='expected line-feed',
      parsers=[
        ('_fimm', 'expected line-feed', lambda: self._reader.consume_string(self._line_feed_predicate, 2, 2))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _line_comment_content_predicate = SimpleClassPredicate.factory(r'^\n')
  def _parse_line_comment_content(self, imin=1, imax=1):
    value = self._reader.parse_type(
      result_type=LineCommentContent,
      error='expected line-comment-content',
      parsers=[
        ('_fimm', 'expected line-comment-content', lambda: self._reader.consume_string(self._line_comment_content_predicate, imin, imax))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _left_to_right_arrow_predicate = StringPredicate(r'->')
  def _parse_left_to_right_arrow(self):
    value = self._reader.parse_type(
      result_type=LeftToRightArrow,
      error='expected left-to-right-arrow',
      parsers=[
        ('_fimm', 'expected left-to-right-arrow', lambda: self._reader.consume_string(self._left_to_right_arrow_predicate, 2, 2))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _single_quote_predicate = StringPredicate(r"'")
  def _parse_single_quote(self):
    value = self._reader.parse_type(
      result_type=SingleQuote,
      error='expected single-quote',
      parsers=[
        ('_fimm', 'expected single-quote', lambda: self._reader.consume_string(self._single_quote_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _double_quote_predicate = StringPredicate(r'"')
  def _parse_double_quote(self):
    value = self._reader.parse_type(
      result_type=DoubleQuote,
      error='expected double-quote',
      parsers=[
        ('_fimm', 'expected double-quote', lambda: self._reader.consume_string(self._double_quote_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  _hyphen_predicate = StringPredicate(r'-')
  def _parse_hyphen(self):
    value = self._reader.parse_type(
      result_type=Hyphen,
      error='expected hyphen',
      parsers=[
        ('_fimm', 'expected hyphen', lambda: self._reader.consume_string(self._hyphen_predicate, 1, 1))
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_domain(self):
    value = self._reader.parse_type(
      result_type=Domain,
      error='expected domain',
      parsers=[
        ('_fimm', 'expected domain, any of domain-literal-full, domain-literal-min', lambda: self._reader.parse_any([self._parse_domain_literal_full,self._parse_domain_literal_min]))
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_import(self):
    value = self._reader.parse_type(
      result_type=Import,
      error='expected import',
      parsers=[
        ('_fimm', 'expected import, any of import-literal-full, import-literal-min', lambda: self._reader.parse_any([self._parse_import_literal_full,self._parse_import_literal_min]))
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_ww(self):
    value = self._reader.parse_type(
      result_type=Ww,
      error='expected ww',
      parsers=[
        ('', 'expected ws in ww', lambda: self._parse_ws(0, 9223372036854775807)),
        ('', 'expected line-comment in ww', lambda: self._reader.parse_many_wp(self._parse_line_comment, 0, 1)),
      ]
      )
    return value
  def _parse_w_old(self):
    value = self._reader.parse_type(
      result_type=W_old,
      error='expected w_old',
      parsers=[
        ('', 'expected ww in w_old', lambda: self._reader.parse_many_wp(self._parse_ww, 0, 9223372036854775807)),
      ]
      )
    return value
  def _parse_w(self):
    value = self._reader.parse_type(
      result_type=W,
      error='expected w',
      parsers=[
        ('', 'expected <whitespace>', lambda: self._reader.consume_string(WhitespacePredicate(), 0, 9223372036854775807))
      ]
      )
    return value
  def _parse_line_comment(self):
    value = self._reader.parse_type(
      result_type=LineComment,
      error='expected line-comment',
      parsers=[
        ('', 'expected octothorp in line-comment', self._parse_octothorp),
        ('', 'expected line-comment-content in line-comment', lambda: self._parse_line_comment_content(0, 9223372036854775807)),
        ('', 'expected line-feed in line-comment', lambda: self._reader.parse_many_wp(self._parse_line_feed, 0, 1)),
      ]
      )
    return value
  def _parse__id(self):
    value = self._reader.parse_type(
      result_type=_id,
      error='expected _id',
      parsers=[
        ('_fimm', 'expected pseudo-letter in _id', lambda: self._parse_pseudo_letter(1, 9223372036854775807)),
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_id(self):
    value = self._reader.parse_type(
      result_type=Id,
      error='expected id',
      parsers=[
        ('', 'expected w in id', self._parse_w),
        ('_fimm', 'expected _id in id', self._parse__id),
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_variable_prefix(self):
    value = self._reader.parse_type(
      result_type=VariablePrefix,
      error='expected variable-prefix',
      parsers=[
        ('', 'expected w in variable-prefix', self._parse_w),
        ('', 'expected dot in variable-prefix', self._parse_dot),
      ]
      )
    return value
  def _parse_realm_path(self):
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: RealmPath(_fcrd=coord, **kwargs),
      error='expected realm-path',
      parsers=[
        ('', 'expected w in realm-path', self._parse_w),
        ('local', 'expected dot (as local) in realm-path', lambda: self._reader.parse_many_wp(self._parse_dot, 0, 1)),
        ('path', 'expected realm-path-branch (as path) in realm-path', lambda: self._reader.parse_many_wp(self._parse_realm_path_branch, 1, 9223372036854775807)),
      ]
      )
    value = self.interceptor.trigger(self.on_realm_path, value)
    return value
  def _parse_realm_path_branch(self):
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: RealmPathBranch(_fcrd=coord, **kwargs),
      error='expected realm-path-branch',
      parsers=[
        ('', 'expected solidus in realm-path-branch', self._parse_solidus),
        ('realm', 'expected id (as realm) in realm-path-branch', self._parse_id),
      ]
      )
    return value
  def _parse_realm_domain_import(self):
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: RealmDomainImport(_fcrd=coord, **kwargs),
      error='expected realm-domain-import',
      parsers=[
        ('', 'expected w in realm-domain-import', self._parse_w),
        ('', 'expected from in realm-domain-import', self._parse_from),
        ('realm', 'expected realm-path (as realm) in realm-domain-import', self._parse_realm_path),
        ('', 'expected w in realm-domain-import', self._parse_w),
        ('', 'expected left-curly-bracket in realm-domain-import', self._parse_left_curly_bracket),
        ('domains', 'expected import-domain-w (as domains) in realm-domain-import', lambda: self._reader.parse_many_wp(self._parse_import_domain_w, 1, 9223372036854775807)),
        ('', 'expected w in realm-domain-import', self._parse_w),
        ('', 'expected right-curly-bracket in realm-domain-import', self._parse_right_curly_bracket),
      ]
      )
    value = self.interceptor.trigger(self.on_realm_domain_import, value)
    return value
  def _parse_import_domain(self):
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: ImportDomain(_fcrd=coord, **kwargs),
      error='expected import-domain',
      parsers=[
        ('', 'expected import in import-domain', self._parse_import),
        ('domain', 'expected id (as domain) in import-domain', self._parse_id),
        ('as_domain', 'expected import-domain-as (as as_domain) in import-domain', lambda: self._reader.parse_many_wp(self._parse_import_domain_as, 0, 1)),
      ]
      )
    return value
  def _parse_import_domain_w(self):
    value = self._reader.parse_type(
      result_type=ImportDomainW,
      error='expected import-domain-w',
      parsers=[
        ('', 'expected w in import-domain-w', self._parse_w),
        ('_fimm', 'expected import-domain in import-domain-w', self._parse_import_domain),
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_import_domain_as(self):
    value = self._reader.parse_type(
      result_type=ImportDomainAs,
      error='expected import-domain-as',
      parsers=[
        ('', 'expected w in import-domain-as', self._parse_w),
        ('', 'expected as in import-domain-as', self._parse_as),
        ('_fimm', 'expected id in import-domain-as', self._parse_id),
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_domain_declaration(self):
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: DomainDeclaration(_fcrd=coord, **kwargs),
      error='expected domain-declaration',
      parsers=[
        ('id', 'expected domain-declaration-id (as id) in domain-declaration', self._parse_domain_declaration_id),
        ('codomain', 'expected codomain in domain-declaration', lambda: self._reader.parse_many_wp(self._parse_codomain, 0, 1)),
        ('domain', 'expected domain-definition (as domain) in domain-declaration', lambda: self._reader.parse_many_wp(self._parse_domain_definition, 0, 1)),
      ]
      )
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
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_domain_declaration_id(self):
    value = self._reader.parse_type(
      result_type=DomainDeclarationId,
      error='expected domain-declaration-id',
      parsers=[
        ('_fimm', 'expected _id in domain-declaration-id', self._parse__id),
      ]
      ,result_immediate='_fimm'
      )
    value = self.interceptor.trigger(self.on_domain_declaration_id, value)
    return value
  def _parse_domain_definition(self):
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: DomainDefinition(_fcrd=coord, **kwargs),
      error='expected domain-definition',
      parsers=[
        ('', 'expected w in domain-definition', self._parse_w),
        ('', 'expected left-curly-bracket in domain-definition', self._parse_left_curly_bracket),
        ('variables', 'expected variable-declaration (as variables) in domain-definition', lambda: self._reader.parse_many_wp(self._parse_variable_declaration, 0, 9223372036854775807)),
        ('domains', 'expected inner-domain-declaration (as domains) in domain-definition', lambda: self._reader.parse_many_wp(self._parse_inner_domain_declaration, 0, 9223372036854775807)),
        ('transforms', 'expected transform-definition (as transforms) in domain-definition', lambda: self._reader.parse_many_wp(self._parse_transform_definition, 0, 9223372036854775807)),
        ('', 'expected w in domain-definition', self._parse_w),
        ('', 'expected right-curly-bracket in domain-definition', self._parse_right_curly_bracket),
      ]
      )
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
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_expression(self):
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: Expression(_fcrd=coord, **kwargs),
      error='expected expression',
      parsers=[
        ('', 'expected w in expression', self._parse_w),
        ('value', 'expected expression-alt (as value) in expression', self._parse_expression_alt),
      ]
      )
    return value
  def _parse_expression_alt(self):
    value = self._reader.parse_type(
      result_type=ExpressionAlt,
      error='expected expression-alt',
      parsers=[
        ('_fimm', 'expected expression-alt, any of expression-literal, expression-domain', lambda: self._reader.parse_any([self._parse_expression_literal,self._parse_expression_domain]))
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_expression_domain(self):
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: ExpressionDomain(_fcrd=coord, **kwargs),
      error='expected expression-domain',
      parsers=[
        ('domainof', 'expected ampersand (as domainof) in expression-domain', lambda: self._reader.parse_many_wp(self._parse_ampersand, 0, 1)),
        ('id', 'expected id in expression-domain', self._parse_id),
        ('arguments', 'expected expression-arguments (as arguments) in expression-domain', lambda: self._reader.parse_many_wp(self._parse_expression_arguments, 0, 1)),
        ('lookup', 'expected expression-lookup (as lookup) in expression-domain', lambda: self._reader.parse_many_wp(self._parse_expression_lookup, 0, 1)),
      ]
      )
    return value
  def _parse_expression_literal(self):
    value = self._reader.parse_type(
      result_type=ExpressionLiteral,
      error='expected expression-literal',
      parsers=[
        ('_fimm', 'expected expression-literal, any of expression-literal-string, expression-literal-float, expression-literal-integer-decimal', lambda: self._reader.parse_any([self._parse_expression_literal_string,self._parse_expression_literal_float,self._parse_expression_literal_integer_decimal]))
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_expression_literal_integer_decimal(self):
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: ExpressionLiteralIntegerDecimal(_fcrd=coord, **kwargs),
      error='expected expression-literal-integer-decimal',
      parsers=[
        ('minus', 'expected hyphen (as minus) in expression-literal-integer-decimal', lambda: self._reader.parse_many_wp(self._parse_hyphen, 0, 1)),
        ('ipart', 'expected pseudo-number (as ipart) in expression-literal-integer-decimal', lambda: self._parse_pseudo_number(1, 9223372036854775807)),
      ]
      )
    value = self.interceptor.trigger(self.on_integer_decimal, value)
    return value
  def _parse_expression_literal_float(self):
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: ExpressionLiteralFloat(_fcrd=coord, **kwargs),
      error='expected expression-literal-float',
      parsers=[
        ('minus', 'expected hyphen (as minus) in expression-literal-float', lambda: self._reader.parse_many_wp(self._parse_hyphen, 0, 1)),
        ('ipart', 'expected pseudo-number (as ipart) in expression-literal-float', lambda: self._parse_pseudo_number(1, 9223372036854775807)),
        ('', 'expected dot in expression-literal-float', self._parse_dot),
        ('dpart', 'expected pseudo-number (as dpart) in expression-literal-float', lambda: self._parse_pseudo_number(1, 9223372036854775807)),
      ]
      )
    value = self.interceptor.trigger(self.on_float, value)
    return value
  _expression_literal_string_content_predicate = FixedEscapedClassPredicate.factory(r'^"\\', r'\\')
  def _parse_expression_literal_string_content(self, imin=1, imax=1):
    value = self._reader.parse_type(
      result_type=ExpressionLiteralStringContent,
      error='expected expression-literal-string-content',
      parsers=[
        ('_fimm', 'expected expression-literal-string-content', lambda: self._reader.consume_string(self._expression_literal_string_content_predicate, imin, imax))
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_expression_literal_string(self):
    value = self._reader.parse_type(
      result_type=ExpressionLiteralString,
      error='expected expression-literal-string',
      parsers=[
        ('', 'expected double-quote in expression-literal-string', self._parse_double_quote),
        ('_fimm', 'expected expression-literal-string-content in expression-literal-string', lambda: self._parse_expression_literal_string_content(0, 9223372036854775807)),
        ('', 'expected double-quote in expression-literal-string', self._parse_double_quote),
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_expression_argument(self):
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: ExpressionArgument(_fcrd=coord, **kwargs),
      error='expected expression-argument',
      parsers=[
        ('', 'expected variable-prefix in expression-argument', self._parse_variable_prefix),
        ('id', 'expected id in expression-argument', self._parse_id),
        ('', 'expected w in expression-argument', self._parse_w),
        ('', 'expected tilde in expression-argument', self._parse_tilde),
        ('expression', 'expected expression in expression-argument', self._parse_expression),
      ]
      )
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
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_expression_lookup(self):
    value = self._reader.parse_type(
      result_type=ExpressionLookup,
      error='expected expression-lookup',
      parsers=[
        ('', 'expected w in expression-lookup', self._parse_w),
        ('', 'expected solidus in expression-lookup', self._parse_solidus),
        ('_fimm', 'expected expression in expression-lookup', self._parse_expression),
      ]
      ,result_immediate='_fimm'
      )
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
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_variable_definition(self):
    value = self._reader.parse_type(
      result_type=VariableDefinition,
      error='expected variable-definition',
      parsers=[
        ('_fimm', 'expected variable-definition, any of variable-constant, variable-bound', lambda: self._reader.parse_any([self._parse_variable_constant,self._parse_variable_bound]))
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_variable_declaration(self):
    value = self._reader.parse_type(
      result_type=VariableDeclaration,
      error='expected variable-declaration',
      parsers=[
        ('', 'expected variable-prefix in variable-declaration', self._parse_variable_prefix),
        ('', 'expected w in variable-declaration', self._parse_w),
        ('_fimm', 'expected variable-definition in variable-declaration', self._parse_variable_definition),
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_variable_constraints_argument(self):
    value = self._reader.parse_type(
      result_type=VariableConstraintsArgument,
      error='expected variable-constraints-argument',
      parsers=[
        ('', 'expected variable-prefix in variable-constraints-argument', self._parse_variable_prefix),
        ('_fimm', 'expected expression in variable-constraints-argument', self._parse_expression),
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_variable_constraints(self):
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: VariableConstraints(_fcrd=coord, **kwargs),
      error='expected variable-constraints',
      parsers=[
        ('', 'expected w in variable-constraints', self._parse_w),
        ('', 'expected double-colon in variable-constraints', self._parse_double_colon),
        ('', 'expected w in variable-constraints', self._parse_w),
        ('', 'expected left-square-bracket in variable-constraints', self._parse_left_square_bracket),
        ('constraints', 'expected variable-constraints-argument (as constraints) in variable-constraints', lambda: self._reader.parse_many_wp(self._parse_variable_constraints_argument, 1, 9223372036854775807)),
        ('', 'expected right-square-bracket in variable-constraints', self._parse_right_square_bracket),
      ]
      )
    return value
  def _parse_variable_domain(self):
    value = self._reader.parse_type(
      result_type=VariableDomain,
      error='expected variable-domain',
      parsers=[
        ('', 'expected w in variable-domain', self._parse_w),
        ('', 'expected colon in variable-domain', self._parse_colon),
        ('_fimm', 'expected expression in variable-domain', self._parse_expression),
      ]
      ,result_immediate='_fimm'
      )
    return value
  def _parse_variable_bound(self):
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: VariableBound(_fcrd=coord, **kwargs),
      error='expected variable-bound',
      parsers=[
        ('id', 'expected _id (as id) in variable-bound', self._parse__id),
        ('variable_domain', 'expected variable-domain (as variable_domain) in variable-bound', lambda: self._reader.parse_many_wp(self._parse_variable_domain, 0, 1)),
        ('variable_constraints', 'expected variable-constraints (as variable_constraints) in variable-bound', lambda: self._reader.parse_many_wp(self._parse_variable_constraints, 0, 1)),
      ]
      )
    return value
  def _parse_variable_constant(self):
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: VariableConstant(_fcrd=coord, **kwargs),
      error='expected variable-constant',
      parsers=[
        ('id', 'expected _id (as id) in variable-constant', self._parse__id),
        ('', 'expected w in variable-constant', self._parse_w),
        ('', 'expected tilde in variable-constant', self._parse_tilde),
        ('expression', 'expected expression in variable-constant', self._parse_expression),
      ]
      )
    return value
  def _parse_transform_compare(self):
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: TransformCompare(_fcrd=coord, **kwargs),
      error='expected transform-compare',
      parsers=[
        ('', 'expected variable-prefix in transform-compare', self._parse_variable_prefix),
        ('variable', 'expected id (as variable) in transform-compare', self._parse_id),
        ('', 'expected w in transform-compare', self._parse_w),
        ('', 'expected equals-sign in transform-compare', self._parse_equals_sign),
        ('domain', 'expected id (as domain) in transform-compare', self._parse_id),
      ]
      )
    return value
  def _parse_transform_definition(self):
    coord = self._reader.get_coord()
    value = self._reader.parse_type(
      result_type=lambda **kwargs: TransformDefinition(_fcrd=coord, **kwargs),
      error='expected transform-definition',
      parsers=[
        ('', 'expected w in transform-definition', self._parse_w),
        ('', 'expected greater-than-sign in transform-definition', self._parse_greater_than_sign),
        ('compares', 'expected transform-compare (as compares) in transform-definition', lambda: self._reader.parse_many_wp(self._parse_transform_compare, 0, 9223372036854775807)),
        ('', 'expected w in transform-definition', self._parse_w),
        ('', 'expected dollar-sign in transform-definition', self._parse_dollar_sign),
        ('locals', 'expected expression-arguments (as locals) in transform-definition', lambda: self._reader.parse_many_wp(self._parse_expression_arguments, 0, 1)),
        ('expression', 'expected expression in transform-definition', self._parse_expression),
      ]
      )
    return value
Parser = _ParserImpl
