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

def get_effective_error(result):
  # the most reasonable error in the trace is the error that last made every
  # parsers fail. In our case that is the second to last line, because the fer 
  # parser has two main sub parsers, the last being EOF which is completly 
  # unhelpful. The second to last will be the deepest error and will have made
  # all other parsers fail.

  # smallest code to get that is to extract it from the formatted result 
  # (i know its not great)
  return pformat(result).finalize().split("\n")[-2].strip()



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
      log.error(get_effective_error(result))
      exit(1)
    log.debug(pformat(result.value).finalize())
    log.info("Parsed fer file")

main()