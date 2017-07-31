import io
import _pickle
import os
import sys

from fer.ferutil import env, id_generator, logger, spformat
from fer.grammer import civilize_parse_error, compiler, interceptor, parser
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
      what += civilize_parse_error(result)
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
    context = psrhook.context.CompilerContext(i, modparser, parser_class)
    context.on_compilation_done = i.register_trigger()

    loader = psrhook.loader.RealmLoader(context)
    literals = psrhook.literals.Literals(context)
    #varcheck = psrhook.varcheck.VariableAnalysis(context)

    # bootstrap by firing a realm import
    asked_realm = parser.ParseValue(
        value=modparser.RealmDomainImport(
            realm='./'+sys.argv[1], domains=[
                modparser.ImportDomain(
                    _fcrd=common.CompilerCoord(),
                    as_domain=None,
                    domain='Main')
            ],
            _fcrd=common.CompilerCoord()),
        coord=common.CompilerCoord())
    result = i.trigger(parser_class.on_realm_domain_import, asked_realm)
    result = i.trigger(context.on_compilation_done, result)
    log.trace(spformat(result))
    if not result:
      raise CompilationProblem("Could not load input", result)
    log.trace(spformat(getattr(result.value, psrhook.loader.RealmLoader.LOADER_IMPORTED_ATTR, None)))

    log.info("C'est finiii!")
  except CompilationProblem as p:
    log.error(p)
  except:
    # if i is not None and context is not None:
    #   i.trigger(context.on_compiler_problem, parser.ParseError(
    #       error="Compiler exception", coord=common.CompilerCoord()))
    raise