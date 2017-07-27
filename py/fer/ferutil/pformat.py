import os

from . import typecheck
from . import env
from . import logger

log = logger.get_logger()

class PformatState(object):
  def __init__(self):
    self.elems = []
    self.instances = set()
  def add(self, elem, **args):
    #log.trace("PformatState.add({}, {})", repr(elem), repr(args))
    self.elems.append((elem, args))
  def finalize(self, max_depth=None):
    l = {
      "depth": 0,
      "lines": [],
      "line": ""
    }
    def fore(s, args):
      """
        newline, start element on a new line
        indent, add to indentation value (will be used on next line)
      """
      if "newline" in args and args["newline"]:
        if max_depth is None or l["depth"] < max_depth:
          l["lines"].append(l["line"])
        l["line"] = ("  "*l["depth"])
      if "indent" in args:
        l["depth"] += args["indent"]
      l["line"] += s
    for e in self.elems:
      fore(e[0], e[1])
    fore("", {"newline":True}) # flush remainder
    return "\n".join(l["lines"])

def pformat(v, state):
  vformat = getattr(v, "__pformat__", None)
  _id = id(v)
  #log.trace("pformat {} {}", type(v).__name__, _id)
  if _id in state.instances:
    pformat("<pformat detected recursion: {} {}>".format(type(v).__name__, _id), state)
    return
  else:
    state.instances.add(_id)
  if callable(vformat):
      vformat(state)
  elif typecheck.ofinstance(v, tuple):
    state.add("(", indent=1, newline=True)
    for i in v[:-1]:
      pformat(i, state)
      state.add(",")
    if len(v) > 0:
      pformat(v[-1], state)
    state.add("", indent=-1)
    state.add(")", newline=True)
  elif typecheck.ofinstance(v, list):
    vlen = len(v)
    if vlen < 1:
      state.add("[]")
    elif vlen > 1:
      state.add("[", indent=1, newline=True)
      for i in v[:-1]:
        pformat(i, state)
        state.add(",")
      if len(v) > 0:
        pformat(v[-1], state)
      state.add("", indent=-1)
      state.add("]", newline=True)
    else:
      state.add("[", indent=1)
      pformat(v[0], state)
      state.add("]", indent=-1)
  elif typecheck.ofinstance(v, dict):
    vs = list(v.items())
    if len(vs) < 1:
      state.add("{}")
    else:
      state.add("{", indent=1, newline=True)
      for k, i in vs[:-1]:
        state.add("", newline=True)
        pformat(k, state)
        state.add(": ", indent=1)
        pformat(i, state)
        state.add(",", indent=-1)
      if len(vs) > 0:
        state.add("", newline=True)
        pformat(vs[-1][0], state)
        state.add(": ", indent=1)
        pformat(vs[-1][1], state)
      state.add("", indent=-2)
      state.add("}", newline=True)
  else:
    state.add(repr(v))
  state.instances.remove(_id)

def spformat(v):
  state = PformatState()
  pformat(v, state)
  return state.finalize()

EV_PATHREL="PATHREL"
env.vars.register(EV_PATHREL, ".", os.path.abspath)
def spformat_path(path):
  if path:
    return os.path.relpath(path, env.vars.get(EV_PATHREL))
  return path

def pformat_class(members, instance, state):
  state.add(type(instance).__name__, indent=1, newline=True)
  state.add("(")
  for id in members[:-1]:
    state.add(str(id), newline=True)
    state.add("=", indent=1)
    pformat(getattr(instance, id), state)
    state.add(",", indent=-1)
  if len(members) > 0:
    id = members[-1]
    state.add(str(id), newline=True)
    state.add("=", indent=1)
    pformat(getattr(instance, id), state)
    state.add("", indent=-1)
  state.add(")", indent=-1)