
import os

class EnvVars(object):
  def __init__(self):
    self.vars = {}
    self.initialized = False
    self.get = self._get_pre

  def _init_var(self, name):
    val = os.getenv(name, self.vars[name]["default"])
    if callable(self.vars[name]["init"]):
      try:
        tmp = self.vars[name]["init"](val)
      except TypeError:
        log.exception("init function for {} could not be called".format(name))
        raise
      else:
        val = tmp
    self.vars[name] = val

  def register(self, name, default=None, init=None):
    self.vars[str(name)] = {
      "default": default,
      "init": init
    }

  def init(self):
    for k in self.vars:
      self._init_var(k)
    self.initialized = True
    self.get = self._get_post

  def trace(self, log):
    for k, v in self.vars.items():
      log.trace("{} = {}".format(k, repr(v)))

  def _get_pre(self, name):
    raise ValueError("EnvVars has not been initialized")

  def _get_post(self, name):
    return self.vars[name]

vars = EnvVars()