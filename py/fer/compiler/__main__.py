import io
import os
import sys

from fer.ferutil import *
from fer.grammer import *
import varcheck

log = logger.get_logger()

TMPDIR_ENVNAME = "TMPDIR"
TMPDIR_DEFAULT = "/tmp"
TMPSUBSIR_BASE = "fer.{}"
TMPDIR = None
def _tmpdir_init():
  tmpdir = os.getenv(TMPDIR_ENVNAME, TMPDIR_DEFAULT)
  tmpsubdir = TMPSUBSIR_BASE.format(id_generator())
  tmpdir = os.path.abspath(os.path.join(tmpdir, tmpsubdir))
  os.makedirs(tmpdir)
  TMPDIR = tmpdir
TMPDIR_INIT = _tmpdir_init

PSRNAME_ENVNAME = "PSRNAME"
PSRNAME_DEFAULT = "Parser"
PSRNAME = None
def _psrname_init():
  psrname = os.getenv(PSRNAME_ENVNAME, PSRNAME_DEFAULT)
  PSRNAME = psrname
PSRNAME_INIT = _psrname_init

PSRMODNAME_ENVNAME = "PSRMODNAME"
PSRMODNAME_DEFAULT = "FerParser"
PSRMODNAME = None
def _psrmodname_init():
  psrmodname = os.getenv(PSRMODNAME_ENVNAME, PSRMODNAME_DEFAULT)
  PSRMODNAME = psrmodname
PSRMODNAME_INIT = _psrmodname_init


PARSER_GRAMMAR = os.path.join(os.path.dirname(__file__), "fer.grammar")


def init_compiler():
  TMPDIR_INIT()
  PSRNAME_INIT()
  PSRMODNAME_INIT()

class CompilationProblem(Exception):
  def __init__(self, what, result):
    # get the first farthest (first highest line,column) error
    # which will indicate what was being parsed
    fcause = result.get_first_deepest_cause()

    # get the farthest (last highest line,column) and highest level (high parser depth)
    # error which will indicate what caused the failure
    lcause = fcause.get_last_deepest_cause()

    super(CompilationProblem, self).__init__(
        "{}:\n{}\n{}".format(what, str(fcause), str(lcause)))

def compile_fer_parser():
  stats, result = compile_parser(PARSER_GRAMMAR, PSRMODNAME, PSRNAME)
  log.debug(spformat(stats))
  if not result:
    raise CompilationProblem("Could not compile fer parser", result)
  return __import__(PSRMODNAME)

def check_variable_semantics(realm):
  result = varcheck.check_realm(realm)
  if not result:
    raise CompilationProblem("Could not verify domain variable semantics", result)
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
      raise CompilationProblem("Could not parse fer file", result)
    
    log.info("Parsed fer file")
    return result.value


def main():
  log.info("Welcome to carbonsteel/fer")
  if len(sys.argv) < 2:
    print "Usage: <input file>"
    exit(1)
  
  init_compiler()

  ferparser = compile_fer_parser()
  realm = parse_fer_input(ferparser)
  something = check_variable_semantics(realm)

  log.info("C'est finiii!")

if __name__ == "__main__":
  try:
    main()
  except CompilationProblem as p:
    log.error(p)
  except:
    log.exception("Unhandled exception in __main__.main()")