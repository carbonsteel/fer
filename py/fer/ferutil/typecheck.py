from .import  errors

def ofinstance(v, typ):
  """ Extends isinstance by allowing a predicate to be used as typ """
  try:
    return isinstance(v, typ)
  except TypeError:
    return typ(v)

class _of_class(object):
  def __init__(self, typ):
    self.typ = typ
  def __call__(self, v):
    if ofinstance(v, self.typ):
      return v
    else:
      raise TypeError("expected value of type %s, got %s instead" % (
          str(self.typ), str(type(v))))

def _of_method(typ):
  def _of_method_what(v):
    if ofinstance(v, typ):
      return v
    raise TypeError("expected value of type %s, got %s instead" % (
        str(typ), str(type(v))))
  return _of_method_what

of = _of_class

class _seq_of_class(object):
  def __init__(self, typ):
    self.typ = typ
  def __call__(self, s):
    try:
      __ = (_ for _ in s)
    except TypeError as e:
      raise TypeError("expected iterable object") from e
    
    for v in s:
      if not ofinstance(v, self.typ):
        raise TypeError("expected iterable of types %s, found %s instead" % (
            str(self.typ), str(type(v)))) from e
    return s

def _seq_of_method(typ):
  def _seq_of_method_what(s):
    try:
      __ = (_ for _ in s)
    except TypeError as e:
      raise errors.GenericError("expected iterable object", e)

    for v in s:
      if not ofinstance(v, typ):
        raise TypeError("expected iterable of types %s, found %s instead" % (str(typ), str(type(v))))
    return s
  return _seq_of_method_what

seq_of = _seq_of_class

class _tuple_of_class(object):
  def __init__(self, *type_list):
    self.type_list = type_list
  def _raise(self, t):
    raise TypeError("expected tuple of types %s, found %s instead" % (
          str(self.type_list), str(t)))
  def __call__(self, t):
    if not ofinstance(t, tuple):
      self._raise(t)
    for v, typ in zip(t, self.type_list):
      if not ofinstance(v, typ):
        self._raise(t)
    return t

def _tuple_of_method(*type_list):
  def _tuple_of_method_what(t):
    if not ofinstance(t, tuple):
      raise errors.GenericError("expected tuple")

    for i in range(0, len(type_list)):
      if not ofinstance(t[i], type_list[i]):
        raise TypeError("expected tuple of types %s, found %s instead" % (str(type_list), str(t)))
    return t
  return _tuple_of_method_what

tuple_of = _tuple_of_class

class _like_class(object):
  def __init__(self, pred, what):
    self.pred = pred
    self.what = what
  def __call__(self, v):
    if self.pred(v):
      return v
    raise TypeError("expected value %s" % self.what)


def _like_method(pred, what):
  def _like_method_what(v):
    if pred(v):
      return v
    raise TypeError("expected value %s" % what)
  return _like_method_what

like = _like_class

def any(v):
  return v