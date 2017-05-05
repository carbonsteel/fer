
import inspect
import logging

from strictargs import *

class LoggerConfig(object):
  def __init__(self, **args):
    StrictNamedArguments({
      "handlers": {}
    })(self, args)

global logger_config
logger_config = None

def init():
  global logger_config
  handler = logging.StreamHandler()
  handler.setLevel(logging.DEBUG)
  formatter = logging.Formatter("%(asctime)s|%(name)s|%(levelname)s|%(message)s")
  handler.setFormatter(formatter)
  logger_config = LoggerConfig(handlers=[handler])

def get_logger():
  global logger_config
  if logger_config is None:
    raise RuntimeError("logger module not initialized")
  frm = inspect.stack()[1]
  module_name = inspect.getmodule(frm[0]).__name__
  logger = logging.getLogger(module_name)
  logger.setLevel(logging.DEBUG)
  for h in logger_config.handlers:
    logger.addHandler(h)
  return logger

