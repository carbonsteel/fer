from __future__ import absolute_import
import io
import os
import sys

from fer.ferutil import env, id_generator, logger, spformat
from fer.grammer import compiler, parser

log = logger.get_logger()

def _tmpdir_init(tmpdir):
  tmpsubdir = "fer.{}".format(id_generator())
  tmpdir = os.path.abspath(os.path.join(tmpdir, tmpsubdir))
  os.makedirs(tmpdir)
  return tmpdir
EV_TMPDIR = "TMPDIR"
env.vars.register(EV_TMPDIR, "/tmp", _tmpdir_init)
EV_PSRNAME = "PSRNAME" 
env.vars.register(EV_PSRNAME, "Parser")
EV_PSRMODNAME = "PSRMODNAME" 
env.vars.register(EV_PSRMODNAME, "FerParser")
EV_PSRGRAMMAR = "PSRGRAMMAR"
env.vars.register(EV_PSRGRAMMAR, os.path.join(os.path.dirname(__file__), "fer.grammar"))


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

def compile_parser():
  log.debug((env.vars.get(EV_PSRGRAMMAR),
      env.vars.get(EV_PSRMODNAME),
      env.vars.get(EV_PSRNAME)))
  stats, result = compiler.compile_parser(
      env.vars.get(EV_PSRGRAMMAR),
      env.vars.get(EV_PSRMODNAME),
      env.vars.get(EV_PSRNAME))
  log.trace(spformat(stats))
  if not result:
    raise CompilationProblem("Could not compile fer parser", result)
  return __import__(env.vars.get(EV_PSRMODNAME))

def parse_input(modparser):
  log.info("Parsing fer file")
  with io.open(sys.argv[1], "rb") as f:
    brf = io.BufferedReader(f)
    r = parser.ParseReader(brf)
    p = getattr(modparser, env.vars.get(EV_PSRNAME))(r)
    result = p()
    log.trace(spformat(r.stats))
    
    if not result:
      raise CompilationProblem("Could not parse fer file", result)
    
    log.info("Parsed fer file")
    return result.value

def check_variable_semantics(realm):
  result = varcheck.check_realm(realm)
  if not result:
    raise CompilationProblem("Could not verify domain variable semantics", result)
  return result.value


def main():
  try:
    log.info("Welcome to carbonsteel/fer")
    if len(sys.argv) < 2:
      print "Usage: <input file>"
      exit(1)

    modparser = compile_parser()
    realm = parse_input(modparser)
    something = check_variable_semantics(realm)

    log.info("C'est finiii!")
  except CompilationProblem as p:
    log.error(p)