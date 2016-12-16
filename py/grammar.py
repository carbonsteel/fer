#!/usr/bin/python2

import io
import re

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

def of(typ):
  def of_what(v):
    if isinstance(v, typ):
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
      if not isinstance(v, typ):
        raise TypeError("expected iterable of types %s, found %s instead" % (str(typ), str(type(v))))
    return s
  return of_what

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
  def __nonzero__(self):
    return self.parse_kind == "value"
  def __str__(self):
    if self.parse_kind == "value":
      return "ok : %s" % str(self.value)
    elif self.parse_kind == "error":
      def rstr(result, depth, _str):
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

  def consume_string(self, minimum_consumed, maximum_consumed, predicate):
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
      if not predicate_result:
        break
      self._stream.read(1) # move forward
      string += byte
      if byte == "\n":
        self.current_coord.line += 1
        self.current_coord.column = 0
      self.current_coord.column += 1
    if not predicate_result and consumed_count <= minimum_consumed:
      error.put(causes=[
          ParseResult(error="unexpected byte `%s'" % byte, coord=self.current_coord)])
      return error
    return ParseResult(value=string, coord=self.current_coord)

class StringPredicate(object):
  def __init__(self, string):
    self.string = string
    self.index = 0
  def __call__(self, byte):
    p = byte == self.string[self.index]
    self.index += 1
    return p
  def what(self):
    wh = "expected byte `%s'" % self.string[max(0, self.index-1)]
    if len(self.string) > 1:
      wh += " from string `%s'" % self.string
    return wh 

def parse_string(**args):
  this = Dummy()
  StrictNamedArguments({
    "reader": {
      "type": of(ParseReader),
    },
    "string": {
      "type": str,
    },
  })(this, args)
  strlen = len(this.string)
  if strlen < 1:
    return ParseResult(value=this.string, coord=this.reader.current_coord)
  pred = StringPredicate(this.string)
  return this.reader.consume_string(strlen, strlen, pred)

class ClassPredicate(object):
  def __init__(self, ccls):
    self.ccls = ccls
    self.re = re.compile("[%s]" % ccls)
  def __call__(self, byte):
    return self.re.match(byte)
  def what(self):
    wh = "expected byte within [%s]" % ccls
    return wh
def parse_class(**args):
  this = Dummy()
  StrictNamedArguments({
    "reader": {
      "type": of(ParseReader),
    },
    "class": {
      "type": str,
    },
  })(this, args)







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
    print parse_string(reader=r, string="\n. ws [ \\n]\n. id  ")
