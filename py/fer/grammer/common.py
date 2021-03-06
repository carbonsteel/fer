import keyword

from .parser import ParseError
from fer.ferutil import *
log = logger.get_logger()


def kebab_to_camel(t): # or how to undigest a desert animal
  parts = []
  for w in t.split("-"):
    parts.append(w[0].upper())
    parts.extend(w[1:])
  return "".join(parts)
def kebab_to_snake(t):
  return "_".join(t.split("-"))

def id_to_var(id):
  _id = kebab_to_snake(id)
  if keyword.iskeyword(_id):
    raise ValueError("Can not use a python keyword as variable: {}".format(_id))
  return _id

def id_to_def(id):
  _id = kebab_to_camel(id)
  if keyword.iskeyword(_id):
    raise ValueError("Can not use a python keyword as definition: {}".format(_id))
  return _id

def id_to_parse(id):
  return "_parse_"+kebab_to_snake(id)
def id_to_predicate(id):
  return "_"+kebab_to_snake(id)+"_predicate"

def civilize_parse_error(result):
  """ return a formatted string containing the (guessed) most relevant
      cause of failure as well as its contextual information.
  """
  what = ""
  top_result = ParseError(error="", causes=[result], coord=result.coord)
  log.trace("Extracting causes")
  # get the first farthest (first highest line,column) error
  # which will indicate what was being parsed (per file)
  fcauses, hcauses = top_result.get_first_deepest_cause()

  for hfile, hc in hcauses.items():
    log.trace("hcause: " + str(hc))

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
    if (lcause 
        or lcause.coord.level < max_level 
        or lcause.coord.file != _fcause.coord.file):
      continue
    if lfile in hcauses:
      hcause = hcauses[lfile]
      pcause = _fcause.get_shallowest_cause_of_coords(hcause.coord, hcause.starting_at)
      log.trace("- pcause: " + str(pcause))
      what += "\np " + str(pcause)
      log.trace("- hcause: " + str(hcause))
      if hcause != _fcause:
        what += "\nh " + str(hcause)
    log.trace("- lcause: " + str(lcause))
    what += "\nl " + str(lcause)
  return what