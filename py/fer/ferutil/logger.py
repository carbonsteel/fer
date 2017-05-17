
import inspect
import logbook

def get_logger():
  frm = inspect.stack()[1]
  module_name = inspect.getmodule(frm[0]).__name__
  return logbook.Logger(module_name)

def init():
  log_handler = logbook.FileHandler('application.log', 'w')
  log_handler.push_application()

init()
