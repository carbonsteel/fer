from __future__ import absolute_import, print_function
import io
import os
import sys
import traceback

from fer.ferutil import env, logger
from fer.compiler import app

EV_LOGLEVEL = "LOGLEVEL"
env.vars.register(EV_LOGLEVEL, "DEBUG", logger.get_level)

# Big problem when Literal definition is not closed
# https://stackoverflow.com/questions/8315389/how-do-i-print-functions-as-they-are-called
def tracefunc(frame, event, arg, indent=[0]):
      if event == "call":
          indent[0] += 2
          print("-" * indent[0] + "> call function", frame.f_code.co_name)
      elif event == "return":
          print("<" + "-" * indent[0], "exit function", frame.f_code.co_name)
          indent[0] -= 2
      return tracefunc

#sys.setprofile(tracefunc)

def init():
  env.vars.init()
  logger.init(env.vars.get(EV_LOGLEVEL))
  modmain = sys.modules[__name__]
  setattr(modmain, "log", logger.get_logger())
  env.vars.forall(lambda k, v: modmain.log.debug("{} = {}".format(k, repr(v))))

if __name__ == "__main__":
  try:
    init()
    try:
      app.main()
    except:
      sys.modules[__name__].log.exception("Unhandled exception in __main__.main()")
  except Exception as e:
    print("Catastrohpic exception during initialization", file=sys.stderr)
    traceback.print_exc(10, sys.stderr)