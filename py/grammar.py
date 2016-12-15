#!/usr/bin/python2

class GenericError(Exception):
  def __init__(self, *causes):
    super(GenericError, self).__init__("\n"+ "\ncaused by\n".join(str(cause) for cause in causes))
    self.causes = causes

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

class Parser(object):
  def __init__(self, stream):
    self.current_coord = ParserCoord()
    self._stream = stream





if __name__ == "__main__":
  c = ParserCoord(line=1, column="2")
  r = ParseResult(value=12, coord=c)
  print r
  e = ParseResult(error="testing", coord=c)
  print e
  f = ParseResult(error="more testing", coord=c, causes=[e,e])
  print f
  g = ParseResult(error="more testing", coord=c, causes=[f,e,e])
  print g
  
