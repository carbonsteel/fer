import os

from . import typecheck
from . import env

class PformatState(object):
  def __init__(self):
    self.elems = []
  def add(self, elem, **args):
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

def pformat(v, state=None):
  if state is None:
    state = PformatState()
  vformat = getattr(v, "__pformat__", None)
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
    state.add("{", indent=1, newline=True)
    vs = list(v.items())
    for k, i in vs[:-1]:
      state.add("", newline=True)
      pformat(k, state)
      state.add(": ")
      pformat(i, state)
      state.add(",")
    if len(vs) > 0:
      state.add("", newline=True)
      pformat(vs[-1][0], state)
      state.add(": ")
      pformat(vs[-1][1], state)
    state.add("", indent=-1)
    state.add("}", newline=True)
  else:
    state.add(repr(v))
  return state

def spformat(v, state=None):
  return pformat(v, state).finalize()

EV_PATHREL="PATHREL"
env.vars.register(EV_PATHREL, ".", os.path.abspath)
def spformat_path(path):
  if path:
    return os.path.relpath(path, env.vars.get(EV_PATHREL))
  return path