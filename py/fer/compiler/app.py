from __future__ import absolute_import
import io
import os
import sys

from fer.ferutil import env, id_generator, logger, spformat, pformat_path
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
  log.trace(spformat(stats))
  if not result:
    raise CompilationProblem("Could not compile fer parser", result)
  return __import__(env.vars.get(EV_PSRMODNAME))

def on_realm_path(realm_path, nocontext):
  if realm_path:
    parts = realm_path.value
    root = parts.local[0] if len(parts.local) > 1 else "/"
    return parser.ParseResult(
        value=root + "/".join(branch.realm for branch in parts.path),
        causes=[realm_path],
        coord=realm_path.coord)
  else:
    return realm_path

def on_realm_domain_import(realm_import_result, modparser):
  if realm_import_result:
    #log.debug(spformat(realm_import_result.value))
    imp = realm_import_result.value
    return parse_realm(imp, modparser)
  return realm_import_result

def realm_to_file(path, realm):
  return os.path.join(path, realm + ".fer")

def find_realm_in_path(realm):
  dirs = env.vars.get(EV_INCPATH)
  # first dir is assumed to be intended local directory (not necessarily '.')
  log.trace(realm)
  if realm[0] == ".":
    dirs = [dirs[0]]
  else: # == '/'
    # remove local directory
    dirs = dirs[1:]
    # strip leading / otherwise join assumes it is root
    realm = realm[1:]
  for dir in dirs:
    path = realm_to_file(dir, realm)
    log.debug("Looking for realm {} at {}", realm, pformat_path(path))
    if os.path.isfile(path):
      return path
  return None

def parse_realm(realm_import, modparser):
  fullpath = find_realm_in_path(realm_import.realm)
  pretty_fullpath = pformat_path(fullpath)
  if fullpath is None:
    return parser.ParseResult(
        error="Could not find realm in path : {}".format(realm_import.realm),
        coord=realm_import._fcrd)
  log.info("Parsing {}", pretty_fullpath)
  with io.open(fullpath, "rb") as f:
    brf = io.BufferedReader(f)
    r = parser.ParseReader(brf, fullpath)
    i = interceptor.Interceptor()
    p_class = getattr(modparser, env.vars.get(EV_PSRNAME))
    i.register(p_class.on_realm_path, on_realm_path)
    i.register(p_class.on_realm_domain_import, on_realm_domain_import, modparser)
    p = p_class(r, i)
    result = p()
    log.trace(spformat(r.stats))
    
    if not result:
      log.trace(spformat(result))
      return parser.ParseResult(
          error="Could not parse realm {}".format(realm_import.realm),
          causes=[result], coord=result.coord)
    
    log.info("Parsed {}", pretty_fullpath)
    log.trace(spformat(result.value))
    #result.causes=[]
    return result

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
    asked_realm = modparser.RealmDomainImport(realm="./" + sys.argv[1], domains=[], _fcrd=parser.ParserCoord())
    result = parse_realm(asked_realm, modparser)
    if not result:
      raise CompilationProblem("Could not load input", result)
    something = check_variable_semantics(result.value)

    log.info("C'est finiii!")
  except CompilationProblem as p:
    log.error(p)