#!/usr/bin/python2

import copy
import io
import logging as log
import pprint
import re
import sys
import types

class GenericError(Exception):
  def __init__(self, *causes):
    super(GenericError, self).__init__("\n"+ "\ncaused by\n".join(str(cause) for cause in causes))
    self.causes = causes

class Dummy(object):
  pass

class StrictNamedArguments(object):
  def __init__(self, definitions, superdefinitions={}, hyperdefinitions={}):
    self._definitions = definitions
    self._superdefinitions = superdefinitions
    self._hyperdefinitions = hyperdefinitions
  @staticmethod
  def _is_required(meta):
    return "default" not in meta
  @staticmethod
  def _default(meta):
    return meta["default"]
  @staticmethod
  def _is_typed(meta):
    return "type" in meta
  @staticmethod
  def _type(meta):
    return meta["type"]
  def __call__(self, instance, args):
    all_definition_id = []
    definitions = self._definitions.copy()
    for id, meta in self._superdefinitions.iteritems():
      for a in meta["arguments"]:
        if a not in definitions:
          raise AttributeError("undefined argument %s in group %s" % (a, id))
      if meta["mutually_exclusive"]:
        found_one = None
        for x in meta["arguments"]:
          if x in args:
            if found_one is None:
              found_one = x
            else:
              raise AttributeError("unexpected argument %s, exclusivity already fullfilled for %s with argument %s" % (
                x, id, found_one
              ))
        if found_one is None:
          raise AttributeError("required exclusive group %s is missing an argument" % (id,))
        else:
          all_definition_id.append(id)
          setattr(instance, id, found_one)
          for x in meta["arguments"]:
            if x == found_one:
              continue
            del definitions[x]

    for id, meta in definitions.iteritems():
      if id not in args:
        if StrictNamedArguments._is_required(meta):
          raise AttributeError("required argument %s is missing" % (id,))
        else:
          all_definition_id.append(id)
          setattr(instance, id, StrictNamedArguments._default(meta))
          continue

      if StrictNamedArguments._is_typed(meta):
        try:
          all_definition_id.append(id)
          setattr(instance, id, StrictNamedArguments._type(meta)(args[id]))
        except (ValueError, TypeError) as e:
          raise GenericError("wrong type for argument %s, expected %s" % (
                  id, str(StrictNamedArguments._type(meta))), e)
      else:
        all_definition_id.append(id)
        setattr(instance, id, args[id])
    if "autostr" not in self._hyperdefinitions or self._hyperdefinitions["autostr"]:
      def autostr(instance, depth):
        attrs = []
        for id in instance.__strict_named_attrs__:
          attrs.append("%s=%s" % (str(id), pformat(getattr(instance, id), depth)))
        return """%s(%s)""" % (type(instance).__name__, ", ".join(attrs))
      setattr(instance, "__strict_named_attrs__", all_definition_id)
      setattr(type(instance), "__pformat__", autostr)

class ParserCoord(object):
  def __init__(self, **args):
    StrictNamedArguments({
      "column": {
        "default": 0,
        "type": int,
      },
      "line": {
        "default": 0,
        "type": int,
      },
    })(self, args)
  def __str__(self):
    return "%d:%d" % (self.line, self.column)
  

def ofinstance(v, typ):
  try:
    return isinstance(v, typ)
  except TypeError:
    return typ(v)

def of(typ):
  def of_what(v):
    if ofinstance(v, typ):
      return v
    raise TypeError("expected value of type %s, got %s instead" % (str(typ), str(type(v))))
  return of_what

def seq_of(typ):
  def of_what(s):
    try:
      __ = (_ for _ in s)
    except TypeError as e:
      raise GenericError("expected iterable object", e)

    for v in s:
      if not ofinstance(v, typ):
        raise TypeError("expected iterable of types %s, found %s instead" % (str(typ), str(type(v))))
    return s
  return of_what

def tuple_of(*type_list):
  def of_what(t):
    if not ofinstance(t, tuple):
      raise GenericError("expected tuple")

    for i in range(0, len(type_list)):
      if not ofinstance(t[i], type_list[i]):
        raise TypeError("expected tuple of types %s, found %s instead" % (str(type_list), str(t)))
    return t
  return of_what

def like(pred, what):
  def of_what(v):
    if pred(v):
      return v
    raise TypeError("expected value %s" % what)
  return of_what

def any(v):
  return v

def pformat(v, depth=0):
  vformat = getattr(v, "__pformat__", None)
  if callable(vformat):
    return vformat(depth)
  if ofinstance(v, tuple):
    return "(%s)" % (", ").join(pformat(i, depth+1) for i in v)
  if ofinstance(v, list):
    return "[%s]" % (",\n" + ("  "*depth)).join(pformat(i, depth+1) for i in v)
  if ofinstance(v, dict):
    return "{%s}" % (",\n" + ("  "*depth)).join("%s: %s" % (pformat(k, depth+1), pformat(i, depth+1)) for k, i in v.iteritems())
  return repr(v)

class ParseResult(object):
  def __init__(self, **args):
    StrictNamedArguments({
      "value": {
      },
      "error": {
        "type": str,
      },
      "coord": {
        "type": of(ParserCoord),
      },
      "causes": {
        "default": [],
        "type": seq_of(ParseResult),
      }
    }, {
      "parse_kind": {
        "arguments": ["value", "error"],
        "mutually_exclusive": True,
      } 
    }, {
      "autostr": False,
    })(self, args)
    # bring value forward 
    if self.parse_kind == "value" and isinstance(self.value, ParseResult):
      self.put(causes=self.value.causes)
      self.value = self.value.value
  def __nonzero__(self):
    return self.parse_kind == "value"
  def __pformat__(self, depth):
    def rstr(result, depth, _str):
      if result.parse_kind == "value":
        _str += "@%d,%d got : %s" % (result.coord.line, result.coord.column, pformat(result.value, depth+1))
      elif result.parse_kind == "error":
        _str += "@%d,%d : %s" % (result.coord.line, result.coord.column, result.error)
      for c in result.causes:
        _str += "\n" + (". "*depth)
        _str += rstr(c, depth+1, "")
      return _str
    return rstr(self, 1, "")
  def put(self, **args):
    that = Dummy()
    StrictNamedArguments({
      "causes": {
        "default": [],
        "type": seq_of(ParseResult),
      }
    })(that, args)
    self.causes.extend(that.causes)

class ParseReader(object):
  def __init__(self, stream):
    self.current_coord = ParserCoord(line=1)
    self._stream = stream
    self.stats = {
      "total_peeks":0,
      "total_consumes": 0,
      "total_backtracks": 0,
      "total_prunes": 0,
    }
    if not self._stream.seekable():
      raise GenericError("programming fault, stream must be seekable")

  def parse_nothing(self, value=None):
    return ParseResult(value=value, coord=self.current_coord)
    
  def parse_type(self, **args):
    this = Dummy()
    StrictNamedArguments({
      "result_type": {
      },
      "error": {
        "type": str,
      },
      "parsers": {
        "type": seq_of(
          tuple_of(
            str,
            str,
            like(callable, "that is callable (and argument-less)"))),
      },
      "result_immediate": {
        "type": str,
        "default": None,
      }
    })(this, args)
    type_args = {}
    parser_errors = ParseResult(error=this.error, coord=self.current_coord)
    for id, error, parser in this.parsers:
      parser_result = parser()
      parser_errors.put(causes=[
          parser_result
      #    ParseResult(error=error, coord=self.current_coord, causes=[parser_result])
      ])
      if not parser_result:
        return parser_errors
      if len(id) > 0:
        type_args[id] = parser_result.value
    value = None
    if this.result_immediate is None:
      value = this.result_type(**type_args)
    else:
      imm = type_args[this.result_immediate]
      try:
        value = this.result_type(imm)
      except TypeError:
        if ofinstance(imm, this.result_type):
          value = imm
        else:
          raise
    return ParseResult(value=value,
        coord=self.current_coord,
        causes=[parser_errors])

  def parse_any(self, parsers):
    errors = ParseResult(error="expected any", coord=self.current_coord)
    for parser in parsers:
      parser_result = self.lookahead(parser)
      if parser_result:
        return parser_result
      errors.put(causes=[parser_result])
    return errors

  def parse_many(self, prefix, parser, minimum_parsed=0, maximum_parsed=sys.maxint):
    results = []
    prefix_errors = ParseResult(error="prefix errors in many",
        coord=self.current_coord)
    parser_errors = ParseResult(error="inner parser errors in many",
        coord=self.current_coord)
    while True:
      count = len(results)
      prefix_result = self.lookahead(prefix)
      prefix_errors.put(causes=[prefix_result])
      if not prefix_result:
        if count >= minimum_parsed:
          return ParseResult(value=results,
              coord=self.current_coord,
              causes=[prefix_errors, parser_errors])
        return ParseResult(
            error="expected at least %d instances, found only %d in many" % (minimum_parsed, count),
            coord=self.current_coord,
            causes=[prefix_errors, parser_errors])
      if count >= maximum_parsed:
        return ParseResult(
            error="expected at most %d instances in many" % (maximum_parsed,),
            coord=self.current_coord,
            causes=[prefix_errors, parser_errors])
      parser_result = parser()
      parser_errors.put(causes=[parser_result])
      if not parser_result:
        return ParseResult(error="expected instance after prefix in many",
            coord=self.current_coord,
            causes=[prefix_errors, parser_errors])
      results.append(parser_result.value)

  def parse_many_wp(self, parser, minimum_parsed=0, maximum_parsed=sys.maxint):
    results = []
    parser_errors = ParseResult(error="inner parser errors in many",
        coord=self.current_coord)
    while True:
      count = len(results)
      if count > maximum_parsed:
        return ParseResult(
            error="expected at most %d instances in many" % (maximum_parsed,),
            coord=self.current_coord,
            causes=[parser_errors])
      parser_result = parser()
      parser_errors.put(causes=[parser_result])
      if not parser_result:
        if count >= minimum_parsed:
          return ParseResult(value=results,
              coord=self.current_coord,
              causes=[parser_errors])
        return ParseResult(
            error="expected at least %d instances, found only %d in many" % (minimum_parsed, count),
            coord=self.current_coord,
            causes=[parser_errors])
      results.append(parser_result.value)
  
  def lookahead(self, parser):
    if not self._stream.readable():
      return ParseResult(error="stream is not readable",
          coord=self.current_coord)
    # save state
    previous_position = self._stream.tell()
    previous_coord = self.current_coord
    result = parser()
    if not result:
      self.stats["total_backtracks"] += 1
      # restore state
      self._stream.seek(previous_position)
      if not self._stream.readable():
        return ParseResult(error="stream is not readable after seeking",
            coord=self.current_coord)
      self.current_coord = previous_coord
    
    return result

  def consume_eof(self):
    peek_bytes = self._stream.peek(1)
    if len(peek_bytes) == 0:
      return ParseResult(value=None, coord=self.current_coord)
    else:
      return ParseResult(error="expected eof", coord=self.current_coord)

  def consume_ws(self):
    def __ws():
      self.consume_string(SimpleClassPredicate(" \n"), 0, sys.maxint)
      return self.consume_string(LineCommentPredicate(), 1, sys.maxint)
    self.parse_many_wp(__ws)

  def consume_token(self, predicate, minimum_consumed=0, maximum_consumed=sys.maxint):
    self.consume_ws()
    return self.consume_string(predicate, minimum_consumed, maximum_consumed)

  def consume_string(self, predicate, minimum_consumed=0, maximum_consumed=sys.maxint):
    string = ""
    error = ParseResult(error=predicate.what(), coord=self.current_coord)
    if not self._stream.readable():
      return ParseResult(error="stream is not readable", coord=self.current_coord)
    predicate_result = None
    consumed_count = 0
    while True:
      peek_bytes = self._stream.peek(predicate.peek_distance)
      if len(peek_bytes) < predicate.peek_distance:
        break
      #if len(peek_bytes) > 1:
      #  error.put(causes=[
      #      ParseResult(error="peek(1) returned more than 1 byte %s" % repr(peek_bytes), coord=self.current_coord)])
      #  return error
      byte = peek_bytes[0]
      consumed_count += 1
      if consumed_count > maximum_consumed:
        break
      #predicaterepr = str(predicate)
      predicate_result = predicate(*(peek_bytes[:predicate.peek_distance]))
      #print "@%d,%d (%s) : %s : %s" % (
      #    self.current_coord.line,
      #    self.current_coord.column,
      #    repr(peek_bytes[:predicate.peek_distance]),
      #    predicate_result,
      #    predicaterepr)
      self.stats["total_peeks"] += 1
      if not predicate_result.consume:
        break
      self.stats["total_consumes"] += 1
      self._stream.seek(io.SEEK_CUR, 1) # move forward
      if not predicate_result.prune:
        string += byte
      else:
        self.stats["total_prunes"] += 1
      self.current_coord = copy.copy(self.current_coord)
      if byte == "\n":
        self.current_coord.line += 1
        self.current_coord.column = 0
      self.current_coord.column += 1
    if predicate_result is None:
      if consumed_count >= minimum_consumed:
        return ParseResult(value=string, coord=self.current_coord)
      error.put(causes=[
          ParseResult(error="unexpected eof", coord=self.current_coord)])
      return error
    if not predicate_result.consume and consumed_count <= minimum_consumed:
      error.put(causes=[
          ParseResult(error="unexpected byte `%s'" % byte, coord=self.current_coord)])
      return error
    return ParseResult(value=string, coord=self.current_coord)

class ConsumePredicateResult(object):
  def __init__(self, **args):
    StrictNamedArguments({
      "prune": {
        "default": False,
        "type": bool,
      },
      "consume": {
        "type": bool,
      }
    })(self, args)

class StringPredicate(object):
  def __init__(self, string):
    self.string = string
    self.index = 0
    self.peek_distance = 1
  def __call__(self, *peek):
    p = peek[0] == self.string[self.index]
    self.index += 1
    return ConsumePredicateResult(consume=p)
  def what(self):
    wh = "expected byte `%s'" % self.string[max(0, self.index-1)]
    if len(self.string) > 1:
      wh += " from string `%s'" % self.string
    return wh
  def __str__(self):
    return """StringPredicate(string=%s)""" % repr(self.string)

class LineCommentPredicate(object):
  def __init__(self):
    self.peek_distance = 1
    self.within_comment = False
  def __call__(self, *peek):
    is_comment = peek[0] == "#"
    is_eol = peek[0] == "\n"
    if is_comment:
      self.within_comment = True
    r = not is_eol and self.within_comment
    return ConsumePredicateResult(consume=r, prune=r)
  def what(self):
    wh = "expected line comment"
    return wh
  def __str__(self):
    return """LineCommentPredicate(within_comment=%s)""" % repr(self.within_comment)


class SimpleClassPredicate(object):
  def __init__(self, ccls):
    self.ccls = ccls
    self.re = re.compile("[%s]" % ccls)
    self.peek_distance = 1
  
  def __call__(self, *peek):
    return ConsumePredicateResult(consume=self.re.match(peek[0]))
  def what(self):
    wh = "expected byte within [%s]" % self.ccls
    return wh
  def __str__(self):
    return """SimpleClassPredicate(ccls=%s)""" % (
        repr(self.ccls),)

class EscapedClassPredicate(object):
  def __init__(self, ccls, cclse):
    self.ccls = ccls
    self.cclse = cclse
    self.re = re.compile("[%s]" % ccls)
    self.ree = re.compile("[%s]" % cclse)
    self.peek_distance = 2
    self.previous_escaped = False
  
  def __call__(self, *peek):
    consume = False
    prune = False
    if self.re.match(peek[0]):
      consume = True
    elif self.previous_escaped:
      self.previous_escaped = False
      consume = True
    elif peek[0] == peek[1] and self.ree.match(peek[0]):
      self.previous_escaped = True
      consume = True
      prune = True
    return ConsumePredicateResult(consume=consume, prune=prune)
  def what(self):
    wh = "expected byte within [%s]" % self.ccls
    return wh
  def __str__(self):
    return """EscapedClassPredicate(ccls=%s, cclse=%s)""" % (
        repr(self.ccls), repr(self.cclse))

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
    return self._reader.parse_many(
        self.parse_definition_prefix,
        self.parse_definition, 1)

def kebab_to_camel(t): # or how to undigest a desert animal
  parts = []
  for w in t.split("-"):
    parts.append(w[0].upper())
    parts.extend(w[1:])
  return "".join(parts)
def kebab_to_snake(t):
  return "_".join(t.split("-"))

def id_to_def(id):
  return kebab_to_camel(id)
def id_to_parse(id):
  return "parse_"+kebab_to_snake(id)
def id_to_parser(id):
  return kebab_to_camel(id)+"Parser"


class GrammarParserCompiler(object):
  def __init__(self, stream, parse_result, parser_name):
    if not parse_result:
      raise ValueError("innapropriate grammar")
    self._stream = stream
    self.grammar = parse_result.value
    self.parser_name = parser_name
    self.known_definitions = {}

  def get_writer(self):
    class _writer(object):
      def __init__(self, stream):
        self._stream = stream
      def __iadd__(self, b):
        self._stream.write(b)
        self._stream.write("\n")
        return self
    return _writer(self._stream)

  def _w_class_for_composite_definition(self, definition):
    if not ofinstance(definition.value, GrammarCompositeDefinition):
      raise ValueError("can't compile class for non composite definition")
    composite = definition.value
    members = {}
    synonym_of = None
    synonym_unicity = True
    synonym_is_str = False
    for d in composite.expression:
      if d["anchor"] is None: # there was no anchor
        continue
      elif d["anchor"] == "": # there was one anchor -> the name is the id
        name = kebab_to_snake(d["identifier"])
        members[name] = {}
      elif d["anchor"] == "@": # two anchors -> the value is bound to the parent
        name = kebab_to_camel(d["identifier"])
        synonym_of = name
        synonym_unicity = d["quantifier"][0] == d["quantifier"][1] == 1
        try:
          synonym_is_str = type(self.known_definitions[d["identifier"]]) == GrammarClassDefinition
        except KeyError:
          raise ValueError("%s is used in %s but is not defined yet" % (d["identifier"], definition.id))
      else:
        name = d["anchor"]
        members[name] = {}
    W = self.get_writer()
    if len(members) > 0:
      W += "class %s(object):" % id_to_def(definition.id)
      W += "  def __init__(self, **args):"
      W += "    grammar.StrictNamedArguments(%s)(self, args)" % repr(members)
    elif synonym_of is None:
      W += "%s = str" % id_to_def(definition.id)
    if synonym_of is not None:
      if synonym_unicity:
        return "%s = %s" % (id_to_def(definition.id), id_to_def(synonym_of))
      elif synonym_is_str:
        return "%s = str" % id_to_def(definition.id)
      else:
        return "%s = list" % id_to_def(definition.id)

  def _w_parser_for_definition(self, definition):
    PARSER_FORMAT = "(%s, 'expected %s', self.%s)"
    is_immediate = False
    W = self.get_writer()
    W += "  def %s(self):" % id_to_parse(definition.id)
    W += "    return self._reader.parse_type("
    W += "      result_type=%s," % id_to_def(definition.id)
    W += "      error='expected %s'," % definition.id
    W += "      parsers=["
    if ofinstance(definition.value, GrammarCompositeDefinition):
      composite = definition.value
      for e in composite.expression:
        if e["identifier"] not in self.known_definitions:
          raise ValueError("%s is used but is not defined" % e["identifier"])
        anchor = None
        if e["anchor"] is None: # there was no anchor
          anchor = ""
        elif e["anchor"] == "": # there was one anchor -> the name is the id
          anchor = kebab_to_snake(e["identifier"])
        elif e["anchor"] == "@": # two anchors -> the value is bound to the parent
          anchor = "_"
          is_immediate = True
        else:
          anchor = e["anchor"] # there was a named anchor -> use that as the id
        inner_parse = None
        if e["quantifier"][0] == e["quantifier"][1] == 1:
          inner_parse = "self." + id_to_parse(e["identifier"])
        elif type(self.known_definitions[e["identifier"]]) == GrammarClassDefinition:
          inner_parse = "lambda: self._reader.consume_string(grammar.SimpleClassPredicate(%s), %d, %d)" % (
            repr(self.known_definitions[e["identifier"]].ccls), e["quantifier"][0], e["quantifier"][1]
          )
        else:
          inner_parse = "lambda: self._reader.parse_many_wp(self.%s, %d, %d)" % (
            id_to_parse(e["identifier"]), e["quantifier"][0], e["quantifier"][1]
          )
        W += "        (%s, 'expected %s in %s', %s)," % (
          repr(anchor), e["identifier"], definition.id, inner_parse
        )
    elif ofinstance(definition.value, GrammarLiteralDefinition):
      W += "        ('_', 'expected %s', lambda: self._reader.consume_string(grammar.StringPredicate(%s), %d, %d))" % (
        definition.id, repr(definition.value.literal), len(definition.value.literal), len(definition.value.literal)
      )
      is_immediate = True
    elif ofinstance(definition.value, GrammarClassDefinition):
      W += "        ('_', 'expected %s', lambda: self._reader.consume_string(grammar.SimpleClassPredicate(%s), 1, 1))" % (
        definition.id, repr(definition.value.ccls)
      )
      is_immediate = True
    else:
      raise ValueError("this should never happen (unless a new Grammar**Definition is added and not updated here)")
    if is_immediate:
      W += "      ],"
      W += "      result_immediate='_')"
    else:
      W += "      ])"

  def __call__(self):
    W = self.get_writer()
    W += "# AUTOMATICLY GENERATED FILE."
    W += "# ALL CHANGES TO THIS FILE WILL BE DISCARDED."
    W += "import grammar"
    W += "# Classes"
    synonyms = []
    for g in self.grammar:
      if ofinstance(g.value, GrammarCompositeDefinition):
        synonym = self._w_class_for_composite_definition(g)
        if synonym is not None:
          synonyms.append(synonym)
      else:
        W += "%s = str" % id_to_def(g.id)
      self.known_definitions[g.id] = g.value
    for s in synonyms:
      W += s
    
    W += "# Main parser"
    W += "class %s(object):" % id_to_parser(self.parser_name)
    W += "  def __init__(self, reader):"
    W += "    self._reader = reader"
    W += "  def __call__(self):"
    W += "    return self.%s()" % id_to_parse(self.grammar[0].id)
    for g in self.grammar:
      self._w_parser_for_definition(g)
    
    



if __name__ == "__main__":
  #c = ParserCoord(line=1, column="2")
  #r = ParseResult(value=12, coord=c)
  #print r
  #e = ParseResult(error="testing", coord=c)
  #print e
  #f = ParseResult(error="more testing", coord=c, causes=[e,e])
  #print f
  #g = ParseResult(error="more testing", coord=c, causes=[f,e,e])
  #print g
  result = None
  with io.open("fer.grammar", "rb") as f:
    brf = io.BufferedReader(f)
    r = ParseReader(brf)
    gp = GrammarParser(r)
    result = gp()
    r.consume_ws()
    eof_result = r.consume_eof()
    if not eof_result:
      result.put(causes=[eof_result])
    print pformat(r.stats)
  print pformat(result)
  with io.open("ferparser.py", "wb+") as f:
    bwf = io.BufferedWriter(f)
    gpc = GrammarParserCompiler(bwf, result, "Fer")
    gpc()
    bwf.flush()