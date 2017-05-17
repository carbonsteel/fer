
from fer.ferutil import *
from common import *
from parser import *

class GrammarClassDefinition(object):
  def __init__(self, **args):
    StrictNamedArguments({
      "ccls": {
        "type": str,
      },
    })(self, args)

class GrammarLiteralDefinition(object):
  def __init__(self, **args):
    StrictNamedArguments({
      "literal": {
        "type": str,
      },
    })(self, args)

class GrammarDefinition(object):
  def __init__(self, **args):
    StrictNamedArguments({
      "id": {
        "type": str,
      },
      "value": {
      },
    })(self, args)

class GrammarCompositeDefinition(object):
  def __init__(self, **args):
    StrictNamedArguments({
      "expression": {
      },
    })(self, args)

class ExpressionQuantifier(object):
  def __init__(self, **args):
    StrictNamedArguments({
      "expression": {
      },
    })(self, args)


class GrammarParser(object):
  def __init__(self, reader):
    self._reader = reader

  IDENTIFIER_CLASS = "a-zA-Z-_"
  def parse_identifier(self, method=None):
    if method is None:
      method = self._reader.consume_token
    return method(SimpleClassPredicate(self.IDENTIFIER_CLASS), minimum_consumed=1)
  
  
  def parse_class(self):
    return self._reader.parse_type(
      result_type=GrammarClassDefinition,
      error="expected class",
      parsers=[
        ("", "expected class prefix",
          lambda: self._reader.consume_token(StringPredicate("["), 1, 1)),
        ("ccls", "expected class value",
          lambda: self._reader.consume_string(EscapedClassPredicate("^\]\.", "\]\."), 1)),
        ("", "expected class postfix",
          lambda: self._reader.consume_token(StringPredicate("]"), 1, 1)),
    ])
  
  def parse_literal(self):
    return self._reader.parse_type(
      result_type=GrammarLiteralDefinition,
      error="expected literal",
      parsers=[
        ("", "expected literal prefix",
          lambda: self._reader.consume_token(StringPredicate("'"), 1, 1)),
        ("literal", "expected literal value",
          lambda: self._reader.consume_string(EscapedClassPredicate("^'\.", "'\."), 1)),
        ("", "expected literal postfix",
          lambda: self._reader.consume_token(StringPredicate("'"), 1, 1)),
    ])

  def quantifier_tuple(self, value):
    if len(value) == 0:
      return (1, 1)
    if value == "+":
      return (1, sys.maxint)
    if value == "*":
      return (0, sys.maxint)
    if value == "?":
      return (0, 1)

  def parse_quantifier(self):
    return self._reader.parse_type(
      result_type=self.quantifier_tuple,
      result_immediate="_",
      error="expected quantifier",
      parsers=[
        ("_", "expected quantifier symbol",
          lambda: self._reader.consume_string(SimpleClassPredicate("\+\*\?"), 0, 1)),
    ])

  def parse_anchor(self):
    return self._reader.parse_type(
      result_type=str,
      result_immediate="_",
      error="expected anchor",
      parsers=[
        ("", "expected anchor prefix",
          lambda: self._reader.consume_string(StringPredicate("@"), 1, 1)),
        ("_", "expected anchor value",
          lambda: self._reader.parse_any([
            lambda: self._reader.consume_string(StringPredicate("@"), 1, 1),
            lambda: self.parse_identifier(self._reader.consume_string),
            lambda: self._reader.parse_nothing("")
          ]))
    ])

  def parse_expression(self):
    return self._reader.parse_type(
      result_type=dict,
      error="expected expression",
      parsers=[
        ("identifier", "expected expression identifier",
          self.parse_identifier),
        ("quantifier", "expected expression quantifier",
          self.parse_quantifier),
        ("anchor", "expected expression anchor",
          lambda: self._reader.parse_any([self.parse_anchor, self._reader.parse_nothing])),
    ])
  
  def parse_composite(self):
    return self._reader.parse_type(
      result_type=GrammarCompositeDefinition,
      error="expected composite",
      parsers=[
        ("", "expected composite prefix",
          lambda: self._reader.consume_token(StringPredicate("("), 1, 1)),
        ("expression", "expected composite expression",
          lambda: self._reader.parse_many_wp(self.parse_expression, 1)),
        ("", "expected composite postfix",
          lambda: self._reader.consume_token(StringPredicate(")"), 1, 1)),
    ])

  def parse_definition_value(self):
    return self._reader.parse_any([
      self.parse_class,
      self.parse_literal,
      self.parse_composite
    ])

  def parse_definition(self):
    return self._reader.parse_type(
      result_type=GrammarDefinition,
      error="expected definition",
      parsers=[
        ("id", "expected definition identifier",
          self.parse_identifier),
        ("value", "expected definition value",
          self.parse_definition_value),
    ])

  def parse_definition_prefix(self):
    prefix = self._reader.consume_token(StringPredicate("."), 1, 1)
    if not prefix:
      return ParseResult(error="expected definition prefix",
          coord=self._reader.current_coord)
    return prefix

  def __call__(self):
    return self._reader.parse_type(
      result_type=list,
      error='expected grammar',
      result_immediate='_',
      parsers=[
        ('_', 'expected definition in grammar', lambda: self._reader.parse_many(self.parse_definition_prefix, self.parse_definition, 1)),
        ('', 'expected whitespace', self._reader.consume_ws),
        ('', 'expected eof', self._reader.consume_eof),
      ])