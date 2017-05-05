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
  log.debug(pformat(stats))
  if not result:
    log.error(pformat(result))
    exit(1)
  ferparser = __import__(PARSER_MODULE_NAME)
  log.info("Parsing fer file")
  with io.open(sys.argv[1], "rb") as f:
    brf = io.BufferedReader(f)
    r = ParseReader(brf)
    p = ferparser.FerParser(r)
    result = p()
    log.debug(pformat(r.stats))
    if not result:
      log.error(pformat(result))
      exit(1)
    log.debug(pformat(result.value))
    log.info("Parsed fer file")

main()