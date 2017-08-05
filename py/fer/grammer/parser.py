import collections
import io
from itertools import tee
import re
import sys
#import traceback

from fer.ferutil import *
log = logger.get_logger()

class ParseCoordDistance(Comparable):
  NIL = None
  def __init__(self, lines, columns, levels):
    self.lines = lines
    self.columns = columns
    self.levels = levels
  def __lt__(self, other):
    if self.levels < other.levels:
      return True
    if self.levels == other.levels:
      if self.lines < other.lines:
        return True
      if self.lines == other.lines:
        return self.columns < other.columns
    return False
  def __str__(self):
    return "ParseCoordDistance(levels={}, columns={}, lines={})".format(self.levels, self.columns, self.lines)
ParseCoordDistance.NIL = ParseCoordDistance(levels=0, columns=0, lines=0)

class ParseCoord(Comparable):
  def __init__(self, file, line, column, level=1):
    self.file = file
    self.line = line
    self.column = column
    self.level = level
  def __str__(self):
    return "{}:{}:{}^{}".format(spformat_path(self.file), self.line, self.column, self.level)
  def localstr(self):
    return "{}:{}".format(self.line, self.column)
  def __lt__(self, other):
    if self.level < other.level:
      return True
    if self.level == other.level:
      if self.line < other.line:
        return True
      if self.line == other.line:
        return self.column < other.column
    return False

  def __sub__(self, other):
    return ParseCoordDistance(lines=self.line - other.line,
        columns=self.column - other.column,
        levels=self.level - other.level)

  def __pformat__(self, state):
    state.add(str(self))
  def copy(self):
    #return fastcopy.deepcopy(self)
    cls = self.__class__
    cpy = cls.__new__(cls)
    cpy.__dict__.update(self.__dict__)
    return cpy
  def levelup(self):
    cpy = self.copy()
    cpy.level += 1
    return cpy

class ParseResultBase(object):
  _COUNTER = 0
  def __init__(self, coord, causes):
    self.coord = coord
    self.causes = [] if causes is None else causes
    ParseResultBase._COUNTER += 1
    self.uid = ParseResultBase._COUNTER
  def __bool__(self):
    raise NotImplementedError()
  def __str__(self):
    raise NotImplementedError()
  def __pformat__(self, state):
    raise NotImplementedError()
  def size(self):
    raise NotImplementedError()
  def get_shallowest_cause_of_coords(self, coord, starting_at):
    for c in self.causes:
      log.trace("{} ({}) {} ({})", c.coord, coord.localstr(), getattr(c, 'starting_at', None), starting_at.localstr())
      if not c and c.coord == coord and c.starting_at == starting_at:
        return c
      else:
        res = c.get_shallowest_cause_of_coords(coord, starting_at)
        if res is not None:
          return res
    return None
  def get_first_deepest_cause(self):
    res = collections.OrderedDict()
    hyper = collections.OrderedDict()
    self._get_first_deepest_cause(res, hyper)
    return res, hyper
  def _get_first_deepest_cause(self, files, hyper):
    for c in self.causes:
      if c.coord.file not in files:
        files[c.coord.file] = c
        hyper[c.coord.file] = c
      elif ((c.coord > files[c.coord.file].coord and c.size() > files[c.coord.file].size())
          or (c.coord == files[c.coord.file].coord
              and c.size() <= files[c.coord.file].size()
              and c.size() > ParseCoordDistance.NIL
              )):
        if c.uid < files[c.coord.file].uid:
          files[c.coord.file] = c
        else:
          hyper[c.coord.file] = c
      # log.trace("c {} {}", c.coord, c.size())
      # log.trace("f {} {}", files[c.coord.file].coord, files[c.coord.file].size())
      c._get_first_deepest_cause(files, hyper)
  def get_last_deepest_cause(self):
    res = collections.OrderedDict()
    max_level = self._get_last_deepest_cause(res)
    return res, max_level
  def _get_last_deepest_cause(self, files):
    max_level = 0
    for c in self.causes:
      if (c.coord.file not in files
          or (c.coord > files[c.coord.file].coord
            or (c.coord == files[c.coord.file].coord
                and c.uid > files[c.coord.file].uid))):
        files[c.coord.file] = c
        if c.coord.level > max_level:
          max_level = c.coord.level
      level = c._get_last_deepest_cause(files)
      if level > max_level:
        max_level = level
    return max_level

class ParseValue(ParseResultBase):
  def __init__(self, value, coord, causes=None):
    super().__init__(coord, causes)
    #log.trace('ParseValue {} {} __init__ called from \n{}', id(self), self.uid, "".join(traceback.format_stack()[:-1]))
    self.value = value
  def __bool__(self):
    return True
  def __str__(self):
    return "+ {}@{} got : ".format(self.uid, self.coord)
  def __pformat__(self, state):
    #log.trace('ParseValue {} {} __pformat__ called', id(self), self.uid)
    state.add(str(self), indent=1, newline=True)
    pformat(self.value, state)
    for c in self.causes:
      pformat(c, state)
    state.add("", indent=-1)
    #log.trace('ParseValue {} {} __pformat__ done', id(self), self.uid)
  def size(self):
    return ParseCoordDistance.NIL

class ParseError(ParseResultBase):
  def __init__(self, error, coord, causes=None, starting_at=None):
    super().__init__(coord, causes)
    #log.trace('ParseError {} {} __init__ called from \n{}', id(self), self.uid, "".join(traceback.format_stack()[:-1]))
    self.error = error
    if starting_at is None:
      self.starting_at = coord
    else:
      self.starting_at = starting_at
  def __bool__(self):
    return False
  def __str__(self):
    if self.coord == self.starting_at:
      return "- {}@{} : {}".format(self.uid, self.coord, self.error)
    else:
      return "- {}@{} : {} starting at {}".format(self.uid, self.coord, self.error, self.starting_at.localstr())
  def __pformat__(self, state):
    #log.trace('ParseError {} {} __pformat__ called', id(self), self.uid)
    state.add(str(self), indent=1, newline=True)
    for c in self.causes:
      pformat(c, state)
    state.add("", indent=-1)
    #log.trace('ParseError {} {} __pformat__ done', id(self), self.uid)
  def size(self):
    return self.coord - self.starting_at

class ParseStreamValidatorError(Exception):
  pass

class ParseStreamValidator(object):
  def __call__(self, stream):
    log.debug('ParseStreamValidator checking a {}'.format(type(stream).__name__))

    if not stream.readable():
      raise ParseStreamValidatorError("Underlying stream is not readable")

    if not stream.seekable():
      raise ParseStreamValidatorError("Underlying stream is not seekable")

    self._has_method(stream, 'read')
    self._has_method(stream, 'seek')
    self._has_method(stream, 'tell')
    return stream

  def _has_method(self, stream, name):
    if hasattr(stream, name):
      log.debug('Underlying stream has method [{}]'.format(name))
    else:
      err = 'Underlying stream is missing method [{}]'.format(name)
      log.debug(err)
      raise ParseStreamValidatorError(err)

class ParseReader(object):
  def __init__(self, stream, stream_name):
    self._current_coord = ParseCoord(column=1, line=1, file=stream_name)
    self._stream = ParseStreamValidator()(stream)
    self.stats = {
      "meta": {
        "name": stream_name
      },
      "total_peeks":0,
      "total_consumes": 0,
      "total_backtracks": 0,
      "total_prunes": 0,
      "total_consumed": 0
    }

  def get_coord(self):
    # return self.current_coord.copy()
    # if self._current_coord_cache is None:
    #   cpy = self.current_coord.copy()
    #   self._current_coord_cache = cpy
    return self._current_coord


  def parse_nothing(self, value=None):
    return ParseValue(value=value, coord=self._current_coord)
  
  def parse_type(self, result_type, error, parsers, result_immediate=None):
    type_args = {}
    begin_coord = self._current_coord
    parser_errors = ParseError(error=error, coord=begin_coord, starting_at=begin_coord)
    for i in range(0, len(parsers)):
      id, error, parser = parsers[i]
      #log.debug("parse_type trying %s %s:%s"%(str(self._current_coord),repr(id),repr(error)))
      parser_result = parser()
      parser_errors.causes.append(parser_result)
      parser_errors.coord = self._current_coord
      if not parser_result:
        parser_result.error += " ({})".format(error)
        return parser_errors
      if id:
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
    errors = ParseError(error="expected any", coord=self._current_coord, starting_at=self._current_coord)
    for parser in parsers:
      parser_result = self.lookahead(parser)
      if not parser_result:
        errors.causes.append(parser_result)
        errors.coord = self._current_coord
        continue
      else:
        parser_result.causes.append(errors)
        return parser_result
    return errors

  def parse_many(self, prefix, parser, minimum_parsed=0, maximum_parsed=sys.maxsize):
    results = []
    begin_coord = self._current_coord
    prefix_errors = ParseError(error="prefix errors in many",
        coord=begin_coord)
    parser_errors = ParseError(error="inner parser errors in many",
        coord=begin_coord)
    count = 0
    while True:
      prefix_result = self.lookahead(prefix)
      prefix_errors.causes.append(prefix_result)
      if not prefix_result:
        if count >= minimum_parsed:
          return ParseValue(value=self._maybe_many(results, maximum_parsed),
              coord=begin_coord,
              causes=[prefix_errors, parser_errors])
        return ParseError(
            error="expected at least %d instances, found only %d in many" % (minimum_parsed, count),
            coord=self._current_coord,
            causes=[prefix_errors, parser_errors])
      if count >= maximum_parsed:
        return ParseError(
            error="expected at most %d instances in many" % (maximum_parsed,),
            coord=self._current_coord,
            causes=[prefix_errors, parser_errors])
      parser_result = parser()
      parser_errors.causes.append(parser_result)
      if not parser_result:
        return ParseError(error="expected instance after prefix in many",
            coord=self._current_coord,
            causes=[prefix_errors, parser_errors])
      results.append(parser_result.value)
      count += 1

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
    begin_coord = self._current_coord
    parser_errors = ParseError(error="inner parser errors in many(min=%d, max=%d)" % (minimum_parsed, maximum_parsed),
        coord=begin_coord, starting_at=begin_coord)
    previous_coord = begin_coord
    count = 0
    while True:
      if count == maximum_parsed:
        return ParseValue(
            value=self._maybe_many(results, maximum_parsed),
            coord=begin_coord,
            causes=[parser_errors])
      parser_result = self.lookahead(parser)
      parser_errors.causes.append(parser_result)
      parser_errors.coord = self._current_coord
      if (not parser_result) or (self._current_coord == previous_coord):
        # bad parse or nothing was successfully parsed
        if count >= minimum_parsed:
          return ParseValue(value=self._maybe_many(results, maximum_parsed),
              coord=begin_coord,
              causes=[parser_errors])
        else:
          return ParseError(
              error="expected at least %d instances, found only %d in many" % (minimum_parsed, count),
              coord=self._current_coord,
              causes=[parser_errors],
              starting_at=begin_coord)
      results.append(parser_result.value)
      count += 1
      previous_coord = self._current_coord
  
  def lookahead(self, parser):
    # save state
    #log.debug("Lookahead called.")
    previous_position = self._stream.tell()
    previous_coord = self._current_coord
    previous_consumed = self.stats["total_consumed"]
    result = parser()
    if not result:
      # restore state
      #log.debug("Lookahead failed, restoring previous state.")
      self._stream.seek(previous_position)
      self._current_coord = previous_coord
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
      return ParseValue(value=None, coord=self._current_coord)
    else:
      return ParseError(error="expected eof", coord=self._current_coord)

  def consume_token(self, predicate, minimum_consumed=0, maximum_consumed=sys.maxsize):
    return self.parse_type(
      result_type=str,
      error='expected token',
      result_immediate='_',
      parsers=[
        ('', 'expected whitespace before token', lambda: self.consume_string(WhitespacePredicate(), 0, 9223372036854775807)),
        ('_', 'expected token', lambda: self.consume_string(predicate, minimum_consumed, maximum_consumed))
      ])

  def consume_string(self, predicate, minimum_consumed=0, maximum_consumed=sys.maxsize):
    string = []
    begin_coord = self._current_coord
    current_coord = begin_coord.copy()
    error = ParseError(error=predicate.what(), coord=begin_coord, starting_at=begin_coord)
    predicate_result = None
    consumed_count = 0
    consumed = []
    peek = None
    #log.trace("Consume called, {} {} {}", begin_coord, minimum_consumed, maximum_consumed)
    read_tell = None
    peek_tell = None
    eof_error = None
    peek_len = predicate.peek_distance - predicate.read_distance
    while True:
      if consumed_count >= maximum_consumed:
        break
      # emulated peek for streams without readinto()
      read_tell = self._stream.tell()
      read = self._stream.read(predicate.read_distance)
      if peek_len != 0:
        peek_tell = self._stream.tell()
        peek = self._stream.read(peek_len)
        peek = read + peek
      else:
        peek = read
      self.stats["total_peeks"] += 1
      #log.trace("Peeked `{}'", peek)
      # failed to peek as far as requested
      if len(peek) < predicate.peek_distance:
        #log.trace("Early eof")
        eof_error = ParseError(error="unexpected eof after {}".format(repr(peek)), coord=begin_coord, starting_at=begin_coord)
        error.causes.append(eof_error)
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
        consumed_count += predicate.read_distance
        consumed.append(read)
        if peek_len != 0:
          self._stream.seek(peek_tell)
        continue
      if predicate_result.consume:
        self.stats["total_consumes"] += 1
        consumed_count += predicate.read_distance
        if predicate.enabled_results.prune:
          consumed.append(read)
        string.append(read)
        if peek_len != 0:
          self._stream.seek(peek_tell)
      else:
        self._stream.seek(read_tell)
        break
    if not predicate.enabled_results.prune:
      consumed = string
    lineparts = ''.join(consumed).split("\n")
    countparts = len(lineparts)
    #log.trace("Coord calc with {} {} {}", self._current_coord, repr(lineparts), repr(countparts))
    if countparts > 1:
      current_coord.line += countparts - 1
      current_coord.column = 1
    current_coord.column += len(lineparts[-1])
    #log.trace("Coord calc result {}", self._current_coord)
    self._current_coord = current_coord
    if eof_error is not None:
      eof_error.coord = current_coord
    error.coord = current_coord
    if consumed_count >= minimum_consumed:
      #log.trace("ok, count ({}) >= min ({})", consumed_count, minimum_consumed)
      self.stats["total_consumed"] += consumed_count
      return ParseValue(value=''.join(string), coord=begin_coord, causes=[error])
    else:
      #log.trace("unexpected terminal `{}'", peek)
      error.causes.append(ParseError(
          error="unexpected terminal {}".format(repr(peek)),
          coord=current_coord, starting_at=begin_coord))
      self._stream.seek(read_tell)
      return error

ConsumePredicateResult = collections.namedtuple('ConsumePredicateResult', ['consume', 'prune'])

class StringPredicate(object):
  enabled_results = ConsumePredicateResult(consume=True, prune=False)
  def __init__(self, string):
    self.string = string
    self.read_distance = self.peek_distance = len(self.string)
    self._what = "expected string {}".format(repr(self.string))
  def __call__(self, peek):
    return ConsumePredicateResult(consume=peek == self.string, prune=False)
  def __str__(self):
    return 'StringPredicate(string={}, read_distance={}, peek_distance={})'.format(
        repr(self.string), repr(self.read_distance), repr(self.peek_distance))
  def what(self):
    return self._what

class WhitespacePredicate(object):
  enabled_results = ConsumePredicateResult(consume=True, prune=True)
  peek_distance = 1
  read_distance = 1
  def __init__(self):
    self.within_comment = False
  def __call__(self, peek):
    if self.within_comment:
      self.within_comment = peek[0] != "\n"
      return ConsumePredicateResult(consume=True, prune=True)
    elif peek[0] == " " or peek[0] == "\n":
      return ConsumePredicateResult(consume=True, prune=True)
    elif peek[0] == "#":
      self.within_comment = True
      return ConsumePredicateResult(consume=True, prune=True)
    else:
      return ConsumePredicateResult(consume=False, prune=False)
  def what(self):
    return "expected <whitespace>"
  def __str__(self):
    return 'WhitespacePredicate(within_comment={}, read_distance={}, peek_distance={})'.format(
        repr(self.within_comment), repr(self.read_distance), repr(self.peek_distance))


class SimpleClassPredicate(object):
  enabled_results = ConsumePredicateResult(consume=True, prune=False)
  peek_distance = 1
  read_distance = 1
  def __init__(self, cclsre):
    self.re = cclsre
    self._what = "expected terminal matching {}".format(repr(self.re.pattern))

  @staticmethod
  def factory(ccls):
    return SimpleClassPredicate(re.compile("[{}]".format(ccls)))
  
  def __call__(self, peek):
    #log.trace("{} {} {} {}", repr(peek), repr(peek[0]), repr(self.re.pattern), repr(self.re.match(peek)))
    return ConsumePredicateResult(consume=self.re.match(peek), prune=False)
  def what(self):
    return self._what
  def __str__(self):
    return 'SimpleClassPredicate(ccls={}, read_distance={}, peek_distance={})'.format(
        repr(self.re.pattern), repr(self.read_distance), repr(self.peek_distance))

class EscapedClassPredicate(object):
  """ Matches characters of ccls and repetition-escaped characters of cclse
  """
  enabled_results = ConsumePredicateResult(consume=True, prune=True)
  peek_distance = 2
  read_distance = 1
  def __init__(self, ccls, cclse):
    self.ccls = ccls
    self.cclse = cclse
    self.re = re.compile("[%s]" % ccls)
    self.ree = re.compile("[%s]" % cclse)
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
    wh = "expected terminal matching {}".format(repr(self.re.pattern))
    return wh
  def __str__(self):
    return 'EscapedClassPredicate(ccls={}, cclse={}, read_distance={}, peek_distance={})'.format(
        repr(self.ccls), repr(self.cclse), repr(self.read_distance), repr(self.peek_distance))

class FixedEscapedClassPredicate(object):
  """ Matches characters of ccls and cclse-prefixed characters not matching ccls """
  enabled_results = ConsumePredicateResult(consume=True, prune=True)
  peek_distance = 2
  read_distance = 1
  def __init__(self, cclsre, cclsere):
    self.re = cclsre
    self.ree = cclsere
    self.next_escaped = False
    self._what = "expected {}-escaped terminal matching {}".format(repr(self.ree.pattern), repr(self.re.pattern))

  @staticmethod
  def factory(ccls, cclse):
    return FixedEscapedClassPredicate(
        re.compile("[{}]".format(ccls)),
        re.compile("[{}]".format(cclse)))
  
  def __call__(self, peek):
    consume = True
    prune = False
    if self.ree.match(peek[0]) and not self.next_escaped:
      prune = self.next_escaped = not self.re.match(peek[1])
    elif self.re.match(peek[0]):
      pass
    elif self.next_escaped:
      self.next_escaped = False
    else:
      consume = False
    return ConsumePredicateResult(consume=consume, prune=prune)
  def what(self):
    return self._what
  def __str__(self):
    return 'FixedEscapedClassPredicate(ccls={}, cclse={}, read_distance={}, peek_distance={})'.format(
        repr(self.re.pattern), repr(self.ree.pattern), repr(self.read_distance), repr(self.peek_distance))