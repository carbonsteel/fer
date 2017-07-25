import io
import _pickle
import os
import sys

from fer.ferutil import env, id_generator, logger, spformat
from fer.grammer import common, compiler, interceptor, parser
from . import psrhook, common

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
  def __init__(self, what, result=None):
    self.result = result
    if result is not None:
      top_result = parser.ParseError(error="", causes=[result], coord=common.CompilerCoord())
      log.trace("Extracting causes")
      # get the first farthest (first highest line,column) error
      # which will indicate what was being parsed (per file)
      fcauses = top_result.get_first_deepest_cause()

      _fcause = None
      for file, fcause in fcauses.items():
        if fcause:
          continue
        log.trace("fcause: " + str(fcause))
        what += "\n" + str(fcause)
        _fcause = fcause
      
      # get the farthest (last highest line,column) and highest level (high parser depth)
      # error which will indicate what caused the failure (for the last file only)
      lcauses, max_level = _fcause.get_last_deepest_cause()
      for lfile, lcause in lcauses.items():
        if (lcause[0] 
            or lcause[0].coord.level < max_level 
            or lcause[0].coord.file != _fcause.coord.file):
          continue
        log.trace("- lcause: " + str(lcause[0]))
        what += "\n- " + str(lcause[0])

    super(CompilationProblem, self).__init__(what)

def compile_parser():
  stats, result = compiler.compile_parser(
      env.vars.get(EV_PSRGRAMMAR),
      env.vars.get(EV_PSRMODNAME),
      env.vars.get(EV_PSRNAME))
  log.trace("Grammar compiling statistics {}", logger.LazyFormat(spformat, stats))
  if not result:
    log.trace("Grammar compiling complete result {}", logger.LazyFormat(spformat, result))
    raise CompilationProblem("Could not compile fer parser", result)
  return __import__(env.vars.get(EV_PSRMODNAME))

def main():
  i = None
  context = None
  try:
    log.info("Welcome to carbonsteel/fer")
    if len(sys.argv) < 2:
      print("Usage: <input file>")
      return 1

    modparser = compile_parser()
    parser_class = getattr(modparser, env.vars.get(EV_PSRNAME))

    i = interceptor.Interceptor()
    context = psrhook.context.CompilerContext(i, parser_class)
    context.on_compilation_done = i.register_trigger()

    loader = psrhook.loader.RealmLoader(context)
    varcheck = psrhook.varcheck.VariableAnalysis(context)

    # bootstrap by firing a realm import
    asked_realm = parser.ParseValue(
        value=modparser.RealmDomainImport(
            realm="./" + sys.argv[1], domains=[],
            _fcrd=common.CompilerCoord()),
        coord=common.CompilerCoord())
    result = i.trigger(parser_class.on_realm_domain_import, asked_realm)
    result = i.trigger(context.on_compilation_done, result)
    if not result:
      raise CompilationProblem("Could not load input", result)

    log.info("C'est finiii!")
  except CompilationProblem as p:
    log.error(p)
  except:
    # if i is not None and context is not None:
    #   i.trigger(context.on_compiler_problem, parser.ParseError(
    #       error="Compiler exception", coord=common.CompilerCoord()))
    raise