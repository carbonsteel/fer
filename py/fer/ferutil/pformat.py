import typecheck


def pformat(v, depth=0):
  vformat = getattr(v, "__pformat__", None)
  if callable(vformat):
    return vformat(depth)
  if typecheck.ofinstance(v, tuple):
    return "(%s)" % (", ").join(pformat(i, depth+1) for i in v)
  if typecheck.ofinstance(v, list):
    return "[%s]" % (",\n" + ("  "*depth)).join(pformat(i, depth+1) for i in v)
  if typecheck.ofinstance(v, dict):
    return "{%s}" % (",\n" + ("  "*depth)).join("%s: %s" % (pformat(k, depth+1), pformat(i, depth+1)) for k, i in v.iteritems())
  return repr(v)