import copy
import io
import re
import sys

from fer.ferutil import *
log = logger.get_logger()

class ParserCoord(object):
  NIL_STR = "!nil!" # must not be a valid path
  @classmethod
  def nil(cls):
    """ For implementation errors, allows ParseResults to float to the top. """
    return ParserCoord(line=sys.maxsize, column=0, file=cls.NIL_STR)

  # First line begins at 1, first column begins at 1
  def __init__(self, **args):
    StrictNamedArguments({
      "column": {
        "default": 1,
        "type": int,
      },
      "line": {
        "default": 1,
        "type": int,
      },
      "file": {
        "default": "",
        "type": str
      }
    })(self, args)
  def __str__(self):
    if self.file == self.NIL_STR:
      return "!"
    else:
      path = ""
      if len(self.file) > 1:
        path = spformat_path(self.file) + "@"
      return "%s%d:%d" % (path, self.line, self.column)
  def __lt__(self, other):
    if self.line < other.line:
      return True
    if self.line > other.line:
      return False
    return self.column < other.column 
  
  def __eq__(self, other):
    return not self<other and not other<self
  def __ne__(self, other):
    return self<other or other<self
  def __gt__(self, other):
    return other<self
  def __ge__(self, other):
    return not self<other
  def __le__(self, other):
    return not other<self

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
    # ouch, get rid of this dependency defined in the importer (fer.compiler)
    self.__wtf__ = id_generator() + "@" if logger.get_level("INFO") > vars.get("LOGLEVEL") else ""
    # bring value forward 
    if self.parse_kind == "value" and isinstance(self.value, ParseResult):
      self.put(causes=self.value.causes)
      self.value = self.value.value
  def __bool__(self):
    return self.parse_kind == "value"
  def __pformat__(self, state):
    state.add(str(self), indent=1, newline=True)
    if self.parse_kind == "value":
      pformat(self.value, state)
    for c in self.causes:
      c.__pformat__(state)
    state.add("", indent=-1)
  def __str__(self):
    if self.parse_kind == "value":
      return "%s%s got : " % (self.__wtf__, self.coord)
    elif self.parse_kind == "error":
      return "%s%s : %s" % (self.__wtf__, self.coord, self.error)
  def get_first_deepest_cause(self):
    res = {}
    self._get_first_deepest_cause(res)
    return res
  def _get_first_deepest_cause(self, files):
    for c in self.causes:
      if (c.coord.file not in files
          or c.coord > files[c.coord.file].coord):
        files[c.coord.file] = c
      c._get_first_deepest_cause(files)
    
  def get_last_deepest_cause(self):
    res = {}
    self._get_last_deepest_cause(0, res)
    return res
  def _get_last_deepest_cause(self, level, files):
    for c in self.causes:
      if (c.coord.file not in files
          or (c.coord > files[c.coord.file][0].coord
            or (c.coord == files[c.coord.file][0].coord
                and level > files[c.coord.file][1]))):
        files[c.coord.file] = (c, level)
      c._get_last_deepest_cause(level+1, files)
  def put(self, **args):
    that = Dummy()
    StrictNamedArguments({
      "causes": {
        "default": [],
        "type": seq_of(ParseResult),
      }
    })(that, args)
    self.causes.extend(that.causes)

class ParseStreamError(Exception):
  pass

class ParseStream(object):
  def __init__(self, stream):
    self._stream = stream
    log.debug('ParseStream initalized with a {}'.format(type(stream).__name__))

    if not self._stream.readable():
      raise ParseStreamError("Underlying stream is not readable")

    if not self._stream.seekable():
      raise ParseStreamError("Underlying stream is not seekable")

    self._init_method('read')
    self._init_method('seek')
    self._init_method('tell')

  def _init_method(self, name, default=None):
    if hasattr(self._stream, name):
      log.debug('Underlying stream has method [{}]'.format(name))
      setattr(self, name, getattr(self._stream, name, None))
    else:
      err = 'Underlying stream is missing method [{}]'.format(name)
      log.debug(err)
      if default is None:
        raise ParseStreamError(err)
      else:
        setattr(self, name, default)

class ParseReader(object):
  def __init__(self, stream, stream_name):
    self.current_coord = ParserCoord(file=stream_name)
    self._stream = ParseStream(stream)
    self.stats = {
      "total_peeks":0,
      "total_consumes": 0,
      "total_backtracks": 0,
      "total_prunes": 0,
      "total_consumed": 0
    }

  def get_coord(self):
    return copy.deepcopy(self.current_coord)

  def parse_nothing(self, value=None):
    return ParseResult(value=value, coord=self.get_coord())
    
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
      },
      "any": {
        "default": False,
      }
    })(this, args)
    type_args = {}
    begin_coord = self.get_coord()
    parser_errors = ParseResult(error=this.error, coord=begin_coord)
    for id, error, parser in this.parsers:
      #log.debug("parse_type trying %s %s:%s"%(str(self.get_coord()),repr(id),repr(error)))
      parser_result = parser()
      parser_errors.put(causes=[
          parser_result
      #    ParseResult(error=error, coord=self.get_coord(), causes=[parser_result])
      ])
      if not parser_result:
        parser_errors.coord = self.get_coord()
        parser_result.error += " (%s)" % (error,)
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
        coord=begin_coord,
        causes=[parser_errors])

  def parse_any(self, parsers):
    errors = ParseResult(error="expected any", coord=self.get_coord())
    for parser in parsers:
      parser_result = self.lookahead(parser)
      errors.put(causes=[parser_result])
      if not parser_result:
        continue
      else:
        return parser_result
    return errors

  def parse_many(self, prefix, parser, minimum_parsed=0, maximum_parsed=sys.maxsize):
    results = []
    begin_coord = self.get_coord()
    prefix_errors = ParseResult(error="prefix errors in many",
        coord=self.get_coord())
    parser_errors = ParseResult(error="inner parser errors in many",
        coord=self.get_coord())
    while True:
      count = len(results)
      prefix_result = self.lookahead(prefix)
      prefix_errors.put(causes=[prefix_result])
      if not prefix_result:
        if count >= minimum_parsed:
          return ParseResult(value=self._maybe_many(results, maximum_parsed),
              coord=begin_coord,
              causes=[prefix_errors, parser_errors])
        return ParseResult(
            error="expected at least %d instances, found only %d in many" % (minimum_parsed, count),
            coord=self.get_coord(),
            causes=[prefix_errors, parser_errors])
      if count >= maximum_parsed:
        return ParseResult(
            error="expected at most %d instances in many" % (maximum_parsed,),
            coord=self.get_coord(),
            causes=[prefix_errors, parser_errors])
      parser_result = parser()
      parser_errors.put(causes=[parser_result])
      if not parser_result:
        return ParseResult(error="expected instance after prefix in many",
            coord=self.get_coord(),
            causes=[prefix_errors, parser_errors])
      results.append(parser_result.value)

  @staticmethod
  def _maybe_many(results, max):
    """ assumes that : len(results) <= max """
    if max == 1:
      if len(results) < 1:
        return None
      else:
        return results[0]
    else:
      return results

  def parse_many_wp(self, parser, minimum_parsed=0, maximum_parsed=sys.maxsize):
    results = []
    begin_coord = self.get_coord()
    parser_errors = ParseResult(error="inner parser errors in many(min=%d, max=%d)" % (minimum_parsed, maximum_parsed),
        coord=self.get_coord())
    previous_coord = begin_coord
    while True:
      count = len(results)
      if count == maximum_parsed:
        return ParseResult(
            value=self._maybe_many(results, maximum_parsed),
            coord=begin_coord,
            causes=[parser_errors])
      parser_result = self.lookahead(parser)
      parser_errors.put(causes=[parser_result])
      current_coord = self.get_coord()
      if (not parser_result) or (current_coord == previous_coord):
        # bad parse or nothing was successfully parsed
        if count >= minimum_parsed:
          return ParseResult(value=self._maybe_many(results, maximum_parsed),
              coord=begin_coord,
              causes=[parser_errors])
        else:
          return ParseResult(
              error="expected at least %d instances, found only %d in many" % (minimum_parsed, count),
              coord=self.get_coord(),
              causes=[parser_errors])
      results.append(parser_result.value)
      previous_coord = current_coord
  
  def lookahead(self, parser):
    # save state
    previous_position = self._stream.tell()
    previous_coord = self.get_coord()
    result = parser()
    if not result:
      # restore state
      self._stream.seek(previous_position)
      self.current_coord = previous_coord
      self.stats["total_backtracks"] += 1
    return result

  def consume_eof(self):
    return self.lookahead(self._consume_eof)
  def _consume_eof(self):
    peek_bytes = self._stream.read(1)
    if len(peek_bytes) == 0:
      return ParseResult(value=None, coord=self.get_coord())
    else:
      return ParseResult(error="expected eof", coord=self.get_coord())

  def consume_ws (self):
    return self.parse_type(
      result_type=str,
      error='expected w',
      parsers=[
        ('', 'expected ww in w', lambda: self.parse_many_wp(self.parse_ww, 0, 9223372036854775807)),
      ])

  def parse_ww(self):
    return self.parse_type(
      result_type=str,
      error='expected w',
      any=True,
      parsers=[
        ('', 'expected ws in ww', lambda: self.consume_string(SimpleClassPredicate(' \n'), 0, 9223372036854775807)),
        ('', 'expected line-comment in ww', lambda: self.parse_many_wp(self.parse_line_comment, 0, 1)),
      ])

  def parse_line_comment(self):
    return self.parse_type(
      result_type=str,
      error='expected line-comment',
      parsers=[
        ('', 'expected octothorp in line-comment', lambda: self.consume_string(StringPredicate('#'), 1, 1)),
        ('', 'expected line-comment-content in line-comment', lambda: self.consume_string(SimpleClassPredicate('^\\n'), 0, 9223372036854775807)),
        ('', 'expected line-feed in line-comment', lambda: self.consume_string(StringPredicate("\n"), 0, 1)),
      ])

  def consume_token(self, predicate, minimum_consumed=0, maximum_consumed=sys.maxsize):
    return self.parse_type(
      result_type=str,
      error='expected token',
      result_immediate='_',
      parsers=[
        ('', 'expected whitespace before token', self.consume_ws),
        ('_', 'expected token', lambda: self.consume_string(predicate, minimum_consumed, maximum_consumed))
      ])

  def consume_string(self, predicate, minimum_consumed=0, maximum_consumed=sys.maxsize):
    return self.lookahead(lambda: self._consume_string(predicate, minimum_consumed, maximum_consumed))
  def _consume_string(self, predicate, minimum_consumed, maximum_consumed):
    string = ""
    begin_coord = self.get_coord()
    error = ParseResult(error=predicate.what(), coord=self.get_coord())
    predicate_result = None
    consumed_count = 0
    peek = None
    while True:
      peek = self._stream.read(predicate.peek_distance)
      self.stats["total_peeks"] += 1
      # failed to peek as far as requested
      if len(peek) < predicate.peek_distance:
        break
      # send peek to predicate
      # trim peek to requested distance as sometimes the buffer is too long
      predicate_result = predicate(peek[:predicate.peek_distance])
      if predicate_result.prune:
        self.stats["total_prunes"] += 1
        break
      if predicate_result.consume:
        self.stats["total_consumes"] += 1
        consumed_count += predicate.read_distance
        if consumed_count > maximum_consumed:
          break
        read = peek[:predicate.read_distance]
        string += read
        lineparts = read.split("\n")
        countparts = len(lineparts)
        if countparts > 1:
          self.current_coord.line += countparts - 1
          self.current_coord.column = 0
        self.current_coord.column += len(lineparts[-1])
    if predicate_result is None:
      if consumed_count >= minimum_consumed:
        self.stats["total_consumed"] += consumed_count
        return ParseResult(value=string, coord=begin_coord)
      else:
        error.put(causes=[
            ParseResult(error="unexpected eof", coord=begin_coord)])
        return error
    elif not predicate_result.consume and consumed_count <= minimum_consumed:
      error.put(causes=[
          ParseResult(error="unexpected bytes `{}'".format(peek), coord=self.get_coord())])
      return error
    else:
      self.stats["total_consumed"] += consumed_count
      return ParseResult(value=string, coord=begin_coord)

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
    self.read_distance = self.peek_distance = len(self.string)
  def __call__(self, peek):
    p = peek == self.string
    return ConsumePredicateResult(consume=p)
  def what(self):
    return "expected bytestring `%s'" % self.string
  def __str__(self):
    return """StringPredicate(string=%s)""" % repr(self.string)

class LineCommentPredicate(object):
  def __init__(self):
    self.peek_distance = 1
    self.read_distance = 1
    self.within_comment = False
  def __call__(self, peek):
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
    self.read_distance = 1
  
  def __call__(self, peek):
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
    self.read_distance = 1
    self.previous_escaped = False
  
  def __call__(self, peek):
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