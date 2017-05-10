import io
import os
import sys

from fer.ferutil import *
logger.init()
from fer.grammer import *

log = logger.get_logger()

PARSER_NAME = "Fer"
PARSER_MODULE_NAME = "autogen_ferparser"
PARSER_MODULE = PARSER_MODULE_NAME+".py"
PARSER_GRAMMAR = os.path.join(os.path.dirname(__file__), "fer.grammar")

def main():
  log.info("Welcome to carbonsteel/fer")
  if len(sys.argv) < 2:
    print "Usage: <input file>"
    exit(1)
  stats, result = compile_parser(PARSER_GRAMMAR, PARSER_MODULE, PARSER_NAME)
  log.debug(pformat(stats).finalize())
  if not result:
    log.error(pformat(result).finalize())
    exit(1)
  ferparser = __import__(PARSER_MODULE_NAME)
  log.info("Parsing fer file")
  with io.open(sys.argv[1], "rb") as f:
    brf = io.BufferedReader(f)
    r = ParseReader(brf)
    p = ferparser.FerParser(r)
    result = p()
    log.debug(pformat(r.stats).finalize())
    #log.debug(pformat(result).finalize())
    if not result:
      # get the error that caused failure the farthest into the file
      cause = result.get_deepest_cause()
      ff = pformat(cause).finalize()
      f = ff.split("\n")
      # pformat will add a line feed before the failed parser and the last 
      # line will contain the consume error
      if len(f) > 2:
        log.error(f[1].strip())
        log.error(f[-1].strip())
      else:
        log.error(ff)

      exit(1)
    log.debug(pformat(result.value).finalize())
    log.info("Parsed fer file")

main()