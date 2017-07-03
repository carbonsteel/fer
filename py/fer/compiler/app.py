from __future__ import absolute_import
import io
import os
import sys

from fer.ferutil import env, id_generator, logger, spformat
from fer.grammer import common, compiler, interceptor, parser
from . import varcheck 

log = logger.get_logger()

def _tmpdir_init(tmpdir):
  tmpsubdir = "fer.{}".format(id_generator())
  tmpdir = os.path.abspath(os.path.join(tmpdir, tmpsubdir))
  os.makedirs(tmpdir)
  return tmpdir
EV_TMPDIR = "TMPDIR"
env.vars.register(EV_TMPDIR, "/tmp", _tmpdir_init)

def _incpath_init(incpath):
  return [os.path.abspath(dir) for dir in incpath.split(";")]

EV_INCPATH = "INCPATH"
env.vars.register(EV_INCPATH, ".", _incpath_init)

EV_PSRNAME = "PSRNAME" 
env.vars.register(EV_PSRNAME, "Parser")
EV_PSRMODNAME = "PSRMODNAME" 
env.vars.register(EV_PSRMODNAME, "FerParser")
EV_PSRGRAMMAR = "PSRGRAMMAR"
env.vars.register(EV_PSRGRAMMAR, os.path.join(os.path.dirname(__file__), "fer.grammar"))


class CompilationProblem(Exception):
  def __init__(self, what, result=None):
    if result is None:
      super(CompilationProblem, self).__init__(what)
    else:
      # get the first farthest (first highest line,column) error
      # which will indicate what was being parsed
      fcause = result.get_first_deepest_cause()

      # get the farthest (last highest line,column) and highest level (high parser depth)
      # error which will indicate what caused the failure
      lcause = fcause.get_last_deepest_cause()

      super(CompilationProblem, self).__init__(
          "{}:\n{}\n{}".format(what, str(fcause), str(lcause)))

def compile_parser():
  stats, result = compiler.compile_parser(
      env.vars.get(EV_PSRGRAMMAR),
      env.vars.get(EV_PSRMODNAME),
      env.vars.get(EV_PSRNAME))
  log.trace(spformat(stats))
  if not result:
    raise CompilationProblem("Could not compile fer parser", result)
  return __import__(env.vars.get(EV_PSRMODNAME))

def on_realm_import(realm_import_result, modparser):
  if realm_import_result:
    #log.debug(spformat(realm_import_result.value))
    imp = realm_import_result.value
    parse_input(common.realm_to_file(imp.realm), modparser)
  return realm_import_result

def parse_input(path, modparser):
  fullpath = os.path.abspath(path)
  if not os.path.isfile(fullpath):
    raise CompilationProblem("Expected realm at {}".format(fullpath))
  log.info("Parsing {}", fullpath)
  with io.open(path, "rb") as f:
    brf = io.BufferedReader(f)
    r = parser.ParseReader(brf)
    i = interceptor.Interceptor()
    p_class = getattr(modparser, env.vars.get(EV_PSRNAME))
    i.register(p_class.on_realm_import, on_realm_import, modparser)
    p = p_class(r, i)
    result = p()
    log.trace(spformat(r.stats))
    
    if not result:
      log.trace(spformat(result))
      raise CompilationProblem(
          "Could not parse {}".format(fullpath), result)
    
    log.info("Parsed {}", fullpath)
    log.trace(spformat(result.value))
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
    realm = parse_input(sys.argv[1], modparser)
    something = check_variable_semantics(realm)

    log.info("C'est finiii!")
  except CompilationProblem as p:
    log.error(p)