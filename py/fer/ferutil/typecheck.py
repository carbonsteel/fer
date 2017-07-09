from .import  errors

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
      raise errors.GenericError("expected iterable object", e)

    for v in s:
      if not ofinstance(v, typ):
        raise TypeError("expected iterable of types %s, found %s instead" % (str(typ), str(type(v))))
    return s
  return of_what

def tuple_of(*type_list):
  def of_what(t):
    if not ofinstance(t, tuple):
      raise errors.GenericError("expected tuple")

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