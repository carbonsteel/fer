from __future__ import absolute_import
import io
import os

from fer.ferutil import env, logger, spformat, spformat_path
from fer.grammer import parser

log = logger.get_logger()

def _incpath_init(incpath):
  return [os.path.abspath(dir) for dir in incpath.split(";")]

EV_INCPATH = "INCPATH"
env.vars.register(EV_INCPATH, ".", _incpath_init)

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
    log.debug("Looking for realm {} at {}", realm, spformat_path(path))
    if os.path.isfile(path):
      return path
  return None

class RealmLoader(object):
  PARSED_IMPORTED_ATTR = "_RealmLoader_imported"
  def __init__(self, interceptor, parser_class):
    self.interceptor = interceptor
    self.parser_class = parser_class

    self.interceptor.register(self.parser_class.on_realm_path, self.stringnify_realm_path)
    self.interceptor.register(self.parser_class.on_realm_domain_import, self.import_realm)

  def stringnify_realm_path(self, realm_path, nocontext):
    if realm_path:
      parts = realm_path.value
      root = parts.local if parts.local is not None else "/"
      return parser.ParseResult(
          value=root + "/".join(branch.realm for branch in parts.path),
          causes=[realm_path],
          coord=realm_path.coord)
    else:
      return realm_path
    
  def import_realm(self, realm_import_result, nocontext):
    if realm_import_result:
      imp = realm_import_result.value
      import_result = self.parse_realm(imp)
      if not import_result:
        return import_result
      setattr(imp, self.PARSED_IMPORTED_ATTR, import_result.value)
    return realm_import_result

  def parse_realm(self, realm_import):
    fullpath = find_realm_in_path(realm_import.realm)
    pretty_fullpath = spformat_path(fullpath)
    if fullpath is None:
      return parser.ParseResult(
          error="Could not find realm in path : {}".format(realm_import.realm),
          coord=realm_import._fcrd)
    log.info("Parsing {}", pretty_fullpath)
    with io.open(fullpath, "rb") as f:
      brf = io.BufferedReader(f)
      r = parser.ParseReader(brf, fullpath)
      p = self.parser_class(r, self.interceptor)
      result = p()
      log.trace(logger.LazyFormat(spformat, r.stats))
      
      if not result:
        log.trace(logger.LazyFormat(spformat, result))
        return parser.ParseResult(
            error="Could not parse realm {}".format(realm_import.realm),
            causes=[result], coord=result.coord)
      
      log.info("Parsed {}", pretty_fullpath)
      log.trace(logger.LazyFormat(spformat, result.value))
      #result.causes=[]
      return result