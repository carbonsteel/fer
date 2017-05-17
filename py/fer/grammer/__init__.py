
import io

from fer.ferutil import *
from compiler import *
from grammar import *
from parser import *

log = logger.get_logger()

def compile_parser(grammar_file, parser_file, parser_name):
  result = None
  log.info("Parsing grammar file")
  with io.open(grammar_file, "rb") as f:
    brf = io.BufferedReader(f)
    r = ParseReader(brf)
    gp = GrammarParser(r)
    result = gp()
    if not result:
      log.error("Failed to parse grammar file")
    else:
      log.info("Parsed grammar file")
      with io.open(parser_file, "wb+") as f:
        bwf = io.BufferedWriter(f)
        gpc = GrammarParserCompiler(bwf, result, parser_name)
        gpc()
        bwf.flush()
        log.info("Wrote parser file")
  return (r.stats, result)