import io
import os
import sys

from fer.ferutil import *
from fer.grammer import *
import varcheck

log = logger.get_logger()

PARSER_NAME = "Fer"
PARSER_MODULE_NAME = "autogen_ferparser"
PARSER_MODULE = PARSER_MODULE_NAME+".py"
PARSER_GRAMMAR = os.path.join(os.path.dirname(__file__), "fer.grammar")

def log_result_errors(result):
  # get the first farthest (first highest line,column) error
  # which will indicate what was being parsed
  fcause = result.get_first_deepest_cause()
  # get the farthest (last highest line,column) and highest level (high parser depth)
  # error which will indicate what caused the failure
  lcause = fcause.get_last_deepest_cause()
  log.error(str(fcause))
  log.error(str(lcause))

def compile_fer_parser():
  stats, result = compile_parser(PARSER_GRAMMAR, PARSER_MODULE, PARSER_NAME)
  log.debug(spformat(stats))
  if not result:
    log_result_errors(result)
    exit(1)
  return __import__(PARSER_MODULE_NAME)

def check_variable_semantics(realm):
  result = varcheck.check_realm(realm)
  if not result:
    log_result_errors(result)
    exit(1)
  return result.value


def parse_fer_input(ferparser):
  log.info("Parsing fer file")
  with io.open(sys.argv[1], "rb") as f:
    brf = io.BufferedReader(f)
    r = ParseReader(brf)
    p = ferparser.FerParser(r)
    result = p()
    log.debug(spformat(r.stats))
    
    if not result:
      log_result_errors(result)
      exit(1)
    
    log.info("Parsed fer file")
    return result.value

def main():
  log.info("Welcome to carbonsteel/fer")
  if len(sys.argv) < 2:
    print "Usage: <input file>"
    exit(1)
  
  ferparser = compile_fer_parser()
  realm = parse_fer_input(ferparser)
  something = check_variable_semantics(realm)

  log.info("C'est finiii!")

if __name__ == "__main__":
  try:
    main()
  except:
    log.exception("Unhandled exception in __main__.main()")