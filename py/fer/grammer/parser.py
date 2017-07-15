import io
import re
import sys

from fer.ferutil import *
log = logger.get_logger()

class ParseCoord(object):
  def __init__(self, file, line, column):
    self.file = file
    self.line = line
    self.column = column
  def __str__(self):
    return "{}:{}:{}".format(spformat_path(self.file), self.line, self.column)
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
  def __pformat__(self, state):
    state.add(str(self))
  def copy(self):
    cls = self.__class__
    cpy = cls.__new__(cls)
    cpy.__dict__.update(self.__dict__)
    return cpy

class ParseResultBase(object):
  _COUNTER = 0
  def __init__(self, coord, causes):
    self.coord = coord
    self.causes = causes
    ParseResultBase._COUNTER += 1
    self.uid = ParseResultBase._COUNTER
  def __bool__(self):
    raise NotImplementedError()
  def __str__(self):
    raise NotImplementedError()
  def __pformat__(self, state):
    raise NotImplementedError()
  def put(self, causes):
    self.causes.extend(causes)
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

class ParseValue(ParseResultBase):
  def __init__(self, value, coord, causes=[]):
    super().__init__(coord, causes)
    self.value = value
  def __bool__(self):
    return True
  def __str__(self):
    return "{}@{} got : ".format(self.uid, self.coord)
  def __pformat__(self, state):
    state.add(str(self), indent=1, newline=True)
    pformat(self.value, state)
    for c in self.causes:
      c.__pformat__(state)
    state.add("", indent=-1)

class ParseError(ParseResultBase):
  def __init__(self, error, coord, causes=[]):
    super().__init__(coord, causes)
    self.error = error
  def __bool__(self):
    return False
  def __str__(self):
    return "{}@{} : {}".format(self.uid, self.coord, self.error)
  def __pformat__(self, state):
    state.add(str(self), indent=1, newline=True)
    for c in self.causes:
      c.__pformat__(state)
    state.add("", indent=-1)

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
    self.current_coord = ParseCoord(column=1, line=1, file=stream_name)
    self._current_coord_cache = self.current_coord
    self._stream = ParseStream(stream)
    self.stats = {
      "total_peeks":0,
      "total_consumes": 0,
      "total_backtracks": 0,
      "total_prunes": 0,
      "total_consumed": 0
    }

  def get_coord(self):
    return self.current_coord.copy()
    #return fastcopy.deepcopy(self.current_coord)
    if self._current_coord_cache is None:
      cpy = fastcopy.deepcopy(self.current_coord)
      self._current_coord_cache = cpy
    return self._current_coord_cache


  def parse_nothing(self, value=None):
    return ParseValue(value=value, coord=self.get_coord())
  
  def parse_type(self, result_type, error, parsers, result_immediate=None):
    type_args = {}
    begin_coord = self.get_coord()
    parser_errors = ParseError(error=error, coord=begin_coord)
    for id, error, parser in parsers:
      #log.debug("parse_type trying %s %s:%s"%(str(self.get_coord()),repr(id),repr(error)))
      parser_result = parser()
      parser_errors.put(causes=[parser_result])
      if not parser_result:
        parser_errors.coord = self.get_coord()
        parser_result.error += " (%s)" % (error,)
        return parser_errors
      if len(id) > 0:
        type_args[id] = parser_result.value
    value = None
    if result_immediate is None:
      value = result_type(**type_args)
    else:
      imm = type_args[result_immediate]
      try:
        value = result_type(imm)
      except TypeError:
        if ofinstance(imm, result_type):
          value = imm
        else:
          raise
    return ParseValue(value=value,
        coord=begin_coord,
        causes=[parser_errors])

  def parse_any(self, parsers):
    errors = ParseError(error="expected any", coord=self.get_coord())
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
    prefix_errors = ParseError(error="prefix errors in many",
        coord=self.get_coord())
    parser_errors = ParseError(error="inner parser errors in many",
        coord=self.get_coord())
    while True:
      count = len(results)
      prefix_result = self.lookahead(prefix)
      prefix_errors.put(causes=[prefix_result])
      if not prefix_result:
        if count >= minimum_parsed:
          return ParseValue(value=self._maybe_many(results, maximum_parsed),
              coord=begin_coord,
              causes=[prefix_errors, parser_errors])
        return ParseError(
            error="expected at least %d instances, found only %d in many" % (minimum_parsed, count),
            coord=self.get_coord(),
            causes=[prefix_errors, parser_errors])
      if count >= maximum_parsed:
        return ParseError(
            error="expected at most %d instances in many" % (maximum_parsed,),
            coord=self.get_coord(),
            causes=[prefix_errors, parser_errors])
      parser_result = parser()
      parser_errors.put(causes=[parser_result])
      if not parser_result:
        return ParseError(error="expected instance after prefix in many",
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
    parser_errors = ParseError(error="inner parser errors in many(min=%d, max=%d)" % (minimum_parsed, maximum_parsed),
        coord=self.get_coord())
    previous_coord = begin_coord
    while True:
      count = len(results)
      if count == maximum_parsed:
        return ParseValue(
            value=self._maybe_many(results, maximum_parsed),
            coord=begin_coord,
            causes=[parser_errors])
      parser_result = self.lookahead(parser)
      parser_errors.put(causes=[parser_result])
      current_coord = self.get_coord()
      if (not parser_result) or (current_coord == previous_coord):
        # bad parse or nothing was successfully parsed
        if count >= minimum_parsed:
          return ParseValue(value=self._maybe_many(results, maximum_parsed),
              coord=begin_coord,
              causes=[parser_errors])
        else:
          return ParseError(
              error="expected at least %d instances, found only %d in many" % (minimum_parsed, count),
              coord=self.get_coord(),
              causes=[parser_errors])
      results.append(parser_result.value)
      previous_coord = current_coord
  
  def lookahead(self, parser):
    # save state
    #log.debug("Lookahead called.")
    previous_position = self._stream.tell()
    previous_coord = self.get_coord()
    previous_consumed = self.stats["total_consumed"]
    result = parser()
    if not result:
      # restore state
      #log.debug("Lookahead failed, restoring previous state.")
      self._stream.seek(previous_position)
      self.current_coord = previous_coord
      self.stats["total_backtracks"] += 1
      self.stats["total_consumed"] = previous_consumed
    #else:
      #log.debug("Lookahead succeded, moving on.")
    return result

  def consume_eof(self):
    return self.lookahead(self._consume_eof)
  def _consume_eof(self):
    peek_bytes = self._stream.read(1)
    if len(peek_bytes) == 0:
      return ParseValue(value=None, coord=self.get_coord())
    else:
      return ParseError(error="expected eof", coord=self.get_coord())

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
    string = ""
    begin_coord = self.get_coord()
    error = ParseError(error=predicate.what(), coord=self.get_coord())
    predicate_result = None
    consumed_count = 0
    peek = None
    #log.trace("Consume called, {} {} {}", begin_coord, minimum_consumed, maximum_consumed)
    read_tell = None
    peek_tell = None
    while True:
      if consumed_count >= maximum_consumed:
        break
      read_tell = self._stream.tell()
      read = self._stream.read(predicate.read_distance)
      peek_tell = self._stream.tell()
      peek = self._stream.read(predicate.peek_distance - predicate.read_distance)
      peek = read + peek
      self.stats["total_peeks"] += 1
      #log.trace("Peeked `{}'", peek)
      # failed to peek as far as requested
      if len(peek) < predicate.peek_distance:
        #log.trace("Early eof")
        error.put(causes=[
            ParseError(error="unexpected eof", coord=self.get_coord())])
        self._stream.seek(read_tell)
        break
      # send peek to predicate
      # trim peek to requested distance as sometimes the buffer is too long
      #log.trace("Predicate `{}'", str(predicate))
      predicate_result = predicate(peek[:predicate.peek_distance])
      #log.trace("Predicate result `{}'", spformat(predicate_result))
      if predicate_result.prune:
        #log.trace("Pruning")
        self.stats["total_prunes"] += 1
        self._stream.seek(peek_tell)
        continue
      if predicate_result.consume:
        self.stats["total_consumes"] += 1
        consumed_count += predicate.read_distance
        string += read
        lineparts = read.split("\n")
        countparts = len(lineparts)
        #log.trace("Coord calc with {} {} {}", self.get_coord(), repr(lineparts), repr(countparts))
        if countparts > 1:
          self.current_coord.line += countparts - 1
          self.current_coord.column = 1
        self.current_coord.column += len(lineparts[-1])
        self._current_coord_cache = None
        #log.trace("Coord calc result {}", self.get_coord())
        self._stream.seek(peek_tell)
      else:
        self._stream.seek(read_tell)
        break
    if consumed_count >= minimum_consumed:
      #log.trace("ok, count ({}) >= min ({})", consumed_count, minimum_consumed)
      self.stats["total_consumed"] += consumed_count
      return ParseValue(value=string, coord=begin_coord, causes=[error])
    else:
      #log.trace("unexpected bytes `{}'", peek)
      error.put(causes=[
          ParseError(error="unexpected bytes {}".format(repr(peek)), coord=self.get_coord())])
      self._stream.seek(read_tell)
      return error

class ConsumePredicateResult(object):
  def __init__(self, consume, prune=False):
    self.consume = consume
    self.prune = prune

class StringPredicate(object):
  def __init__(self, string):
    self.string = string
    self.read_distance = self.peek_distance = len(self.string)
  def __call__(self, peek):
    p = peek == self.string
    return ConsumePredicateResult(consume=p)
  def __str__(self):
    return 'StringPredicate(string={}, read_distance={}, peek_distance={})'.format(
        repr(self.string), repr(self.read_distance), repr(self.peek_distance))
  def what(self):
    return "expected bytestring `%s'" % self.string

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
    return 'LineCommentPredicate(within_comment={}, read_distance={}, peek_distance={})'.format(
        repr(self.within_comment), repr(self.read_distance), repr(self.peek_distance))


class SimpleClassPredicate(object):
  def __init__(self, ccls):
    self.ccls = ccls
    self.re = re.compile("[%s]" % ccls)
    self.peek_distance = 1
    self.read_distance = 1
  
  def __call__(self, peek):
    #log.trace("{} {} {} {}", repr(peek), repr(peek[0]), repr(self.re.pattern), repr(self.re.match(peek)))
    return ConsumePredicateResult(consume=self.re.match(peek))
  def what(self):
    wh = "expected byte within [%s]" % self.ccls
    return wh
  def __str__(self):
    return 'SimpleClassPredicate(ccls={}, read_distance={}, peek_distance={})'.format(
        repr(self.ccls), repr(self.read_distance), repr(self.peek_distance))

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
    return 'EscapedClassPredicate(ccls={}, cclse={}, read_distance={}, peek_distance={})'.format(
        repr(self.ccls), repr(self.cclse), repr(self.read_distance), repr(self.peek_distance))