
import copy
import io
import re
import sys

from fer.ferutil import *

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