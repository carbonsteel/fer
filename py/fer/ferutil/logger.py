import inspect
import logbook
import sys

def get_level(level_name):
  try:
    return logbook.lookup_level(level_name.upper())
  except LookupError:
    return logbook.ERROR

def get_logger():
  frm = inspect.stack()[1]
  module_name = inspect.getmodule(frm[0]).__name__
  return logbook.Logger(module_name)

class LazyFormat(object):
  def __init__(self, callback, *args, **kwargs):
    self.callback = callback
    self.args = args
    self.kwargs = kwargs
  def __str__(self):
    return self.callback(*self.args, **self.kwargs)

Z = LazyFormat

def init(level):
  #log_handler = logbook.FileHandler('application.log', 'w')
  log_handler = logbook.StreamHandler(sys.stdout, level=level)
  log_handler.push_application()