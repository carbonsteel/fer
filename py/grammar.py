#!/usr/bin/python2

import copy
import io
import re
import sys

class GenericError(Exception):
  def __init__(self, *causes):
    super(GenericError, self).__init__("\n"+ "\ncaused by\n".join(str(cause) for cause in causes))
    self.causes = causes

class Dummy(object):
  pass

class StrictNamedArguments(object):
  def __init__(self, definitions, superdefinitions={}):
    self._definitions = definitions
    self._superdefinitions = superdefinitions
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
          setattr(instance, id, StrictNamedArguments._default(meta))
          continue

      if StrictNamedArguments._is_typed(meta):
        try:
          setattr(instance, id, StrictNamedArguments._type(meta)(args[id]))
        except (ValueError, TypeError) as e:
          raise GenericError("wrong type for argument %s, expected %s" % (
                  id, str(StrictNamedArguments._type(meta))),
              e)
      else:
        setattr(instance, id, args[id])

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

def tuple_of(*types):
  def of_what(t):
    if not ofinstance(t, tuple):
      raise GenericError("expected tuple")

    for i in range(0, len(types)):
      if not ofinstance(t[i], types[i]):
        raise TypeError("expected tuple of types %s, found %s instead" % (str(types), str(t)))
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
    })(self, args)
    # bring value forward 
    if self.parse_kind == "value" and isinstance(self.value, ParseResult):
      self.put(causes=self.value.causes)
      self.value = self.value.value
  def __nonzero__(self):
    return self.parse_kind == "value"
  def __str__(self):
    def rstr(result, depth, _str):
      if result.parse_kind == "value":
        return "ok @%d,%d : %s" % (result.coord.line, result.coord.column, str(result.value))
      elif result.parse_kind == "error":
        _str += "error @%d,%d : %s" % (result.coord.line, result.coord.column, result.error)
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
    if not self._stream.seekable():
      raise GenericError("programming fault, stream must be seekable")
    
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
    })(this, args)
    type_args = {}
    parser_errors = ParseResult(error=this.error, coord=self.current_coord)
    for id, error, parser in this.parsers:
      parser_result = parser()
      parser_errors.put(causes=[
          ParseResult(error=error, coord=self.current_coord, causes=[parser_result])
      ])
      if not parser_result:
        return parser_errors
      if len(id) > 0:
        type_args[id] = parser_result.value
    return ParseResult(value=this.result_type(**type_args),
        coord=self.current_coord,
        causes=[parser_errors])

  def parse_any(self, parsers):
    errors = ParseResult(error="expected any", coord=self.current_coord)
    for parser in parsers:
      parser_result = parser()
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
            causes=[prefix_errors, parser_errors])
      if count >= maximum_parsed:
        return ParseResult(
            error="expected at most %d instances in many" % (maximum_parsed,),
            causes=[prefix_errors, parser_errors])
      parser_result = parser()
      parser_errors.put(causes=[parser_result])
      if not parser_result:
        return ParseResult(error="expected instance after prefix in many",
            coord=self.current_coord,
            causes=[prefix_errors, parser_errors])
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
      # restore state
      self._stream.seek(previous_position)
      if not self._stream.readable():
        return ParseResult(error="stream is not readable after seeking",
            coord=self.current_coord)
      self.current_coord = previous_coord
    
    return result


  def consume_token(self, predicate, minimum_consumed=0, maximum_consumed=sys.maxint):
    self.consume_string(ClassPredicate(" \n"), 0, sys.maxint)
    return self.consume_string(predicate, minimum_consumed, maximum_consumed)

  def consume_string(self, predicate, minimum_consumed, maximum_consumed):
    string = ""
    error = ParseResult(error=predicate.what(), coord=self.current_coord)
    if not self._stream.readable():
      return ParseResult(error="stream is not readable", coord=self.current_coord)
    predicate_result = None
    consumed_count = 0
    while True:
      peek_bytes = self._stream.peek(1)
      if len(peek_bytes) < 1:
        error.put(causes=[
            ParseResult(error="unexpected eof", coord=self.current_coord)])
        return error
      #if len(peek_bytes) > 1:
      #  error.put(causes=[
      #      ParseResult(error="peek(1) returned more than 1 byte %s" % repr(peek_bytes), coord=self.current_coord)])
      #  return error
      byte = peek_bytes[0]
      consumed_count += 1
      if consumed_count > maximum_consumed:
        break
      predicate_result = predicate(byte)
      print "@%d,%d (%s) : %s : %s" % (
          self.current_coord.line,
          self.current_coord.column,
          repr(byte),
          predicate_result,
          predicate)
      if not predicate_result.consume:
        break
      self._stream.seek(io.SEEK_CUR, 1) # move forward
      if not predicate_result.prune:
        string += byte
      self.current_coord = copy.copy(self.current_coord)
      if byte == "\n":
        self.current_coord.line += 1
        self.current_coord.column = 0
      self.current_coord.column += 1
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
  def __str__(self):
    return """ConsumePredicateResult(consume=%s, prune=%s)""" % (self.consume, self.prune)

class StringPredicate(object):
  def __init__(self, string):
    self.string = string
    self.index = 0
  def __call__(self, byte):
    p = byte == self.string[self.index]
    self.index += 1
    return ConsumePredicateResult(consume=p)
  def what(self):
    wh = "expected byte `%s'" % self.string[max(0, self.index-1)]
    if len(self.string) > 1:
      wh += " from string `%s'" % self.string
    return wh
  def __str__(self):
    return """StringPredicate(string="%s")""" % repr(self.string)

class ClassPredicate(object):
  def __init__(self, ccls):
    self.ccls = ccls
    self.re = re.compile("[%s]" % ccls)
    self.previous_byte = None
    self.previous_escaped = False
  
  def __call__(self, byte):
    if self.re.match(byte):
      self.previous_byte = byte
      self.previous_escaped = False
      return ConsumePredicateResult(consume=True)
    elif self.previous_byte == byte:
      if self.previous_escaped:
        return ConsumePredicateResult(consume=False)
      else:
        self.previous_byte = byte
        self.previous_escaped = False
        return ConsumePredicateResult(consume=True, prune=True)
    return ConsumePredicateResult(consume=False)

  def what(self):
    wh = "expected byte within [%s]" % self.ccls
    return wh
  def __str__(self):
    return """ClassPredicate(ccls="%s")""" % repr(self.ccls)

class GrammarClassDefinition(object):
  def __init__(self, **args):
    StrictNamedArguments({
      "ccls": {
        "type": str,
      },
    })(self, args)
  def __str__(self):
    return """GrammarClassDefinition(ccls=[%s])""" % (repr(self.ccls),)

class GrammarLiteralDefinition(object):
  def __init__(self, **args):
    StrictNamedArguments({
      "literal": {
        "type": str,
      },
    })(self, args)
  def __str__(self):
    return """GrammarLiteralDefinition(literal='%s')""" % (repr(self.literal),)

class GrammarDefinition(object):
  def __init__(self, **args):
    StrictNamedArguments({
      "id": {
        "type": str,
      },
      "value": {
      },
    })(self, args)
  def __str__(self):
    return """GrammarDefinition(id="%s", value=%s)""" % (self.id, self.value)

class GrammarCompositeDefinition(object):
  def __init__(self, **args):
    StrictNamedArguments({
      "id": {
        "type": str,
      },
      #todo
    })(self, args)

class GrammarParser(object):
  def __init__(self, reader):
    self._reader = reader

  def parse_identifier(self):
    return self._reader.consume_token(ClassPredicate("a-zA-Z-_"), minimum_consumed=1)
  
  def parse_class(self):
    return self._reader.parse_type(
      result_type=GrammarClassDefinition,
      error="expected class",
      parsers=[
        ("", "expected class prefix",
          lambda: self._reader.consume_token(StringPredicate("["), 1, 1)),
        ("ccls", "expected class value",
          lambda: self._reader.consume_token(ClassPredicate("^\]\."), 1)),
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
          lambda: self._reader.consume_token(ClassPredicate("^'\."), 1)),
        ("", "expected literal postfix",
          lambda: self._reader.consume_token(StringPredicate("'"), 1, 1)),
    ])

  def parse_definition_value(self):
    return self._reader.parse_any([
      self.parse_class,
      self.parse_literal
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
  with io.open("fer.grammar", "rb") as f:
    brf = io.BufferedReader(f)
    r = ParseReader(brf)
    gp = GrammarParser(r)
    print gp()
