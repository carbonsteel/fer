from __future__ import absolute_import
import io
import os
import sys

from fer.ferutil import env, id_generator, logger, spformat
from fer.grammer import common, compiler, interceptor, parser
from . import psrhook 

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
    if result is not None:
      log.trace("Extracting causes")
      # get the first farthest (first highest line,column) error
      # which will indicate what was being parsed (per file)
      fcauses = result.get_first_deepest_cause()

      # get the farthest (last highest line,column) and highest level (high parser depth)
      # error which will indicate what caused the failure (for each file or each cause)
      for file, fcause in fcauses.items():
        if fcause.parse_kind != "error":
          continue
        log.trace("fcause: " + str(fcause))
        what += "\n" + str(fcause)
        lcauses = fcause.get_last_deepest_cause()
        for lfile, lcause in lcauses.items():
          if lcause[0].parse_kind != "error":
            continue
          log.trace("- lcause: " + str(lcause[0]))
          what += "\n- " + str(lcause[0])

    super(CompilationProblem, self).__init__(what)

def compile_parser():
  stats, result = compiler.compile_parser(
      env.vars.get(EV_PSRGRAMMAR),
      env.vars.get(EV_PSRMODNAME),
      env.vars.get(EV_PSRNAME))
  log.trace(logger.LazyFormat(spformat, stats))
  if not result:
    raise CompilationProblem("Could not compile fer parser", result)
  return __import__(env.vars.get(EV_PSRMODNAME))

def main():
  try:
    log.info("Welcome to carbonsteel/fer")
    if len(sys.argv) < 2:
      print "Usage: <input file>"
      return 1

    modparser = compile_parser()
    parser_class = getattr(modparser, env.vars.get(EV_PSRNAME))

    i = interceptor.Interceptor()
    context = psrhook.context.CompilerContext(i, parser_class)
    context.on_compilation_problem = i.register_trigger()

    loader = psrhook.loader.RealmLoader(context)
    varcheck = psrhook.varcheck.VariableAnalysis(context)

    # bootstrap by firing a realm import
    asked_realm = parser.ParseResult(
        value=modparser.RealmDomainImport(
            realm="./" + sys.argv[1], domains=[], _fcrd=parser.ParserCoord()),
        coord=parser.ParserCoord.nil())
    result = i.trigger(parser_class.on_realm_domain_import, asked_realm)
    if not result:
      i.trigger(context.on_compilation_problem, result)
      raise CompilationProblem("Could not load input", result)

    log.info("C'est finiii!")
  except CompilationProblem as p:
    log.error(p)