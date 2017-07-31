import unittest

from fer import EV_LOGLEVEL
from fer.ferutil import env, logger
env.vars.init()
logger.init(env.vars.get(EV_LOGLEVEL))

if __name__ == '__main__':
  unittest.main()