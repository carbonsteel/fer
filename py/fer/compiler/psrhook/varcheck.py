
from fer.ferutil import *
from fer.grammer import ParseResult

log = logger.get_logger()

class VariableAnalysis(object):
  def check_realm(self, realm):
    #log.debug(spformat(realm))
    return ParseResult(error="Not implemented", coord=realm._fcrd)

def check_realm(realm):
  va = VariableAnalysis()
  return va.check_realm(realm)

def check_variable_semantics(realm):
  log.debug(spformat(realm))
  result = varcheck.check_realm(realm)
  if not result:
    raise CompilationProblem("Could not verify domain variable semantics", result)
  return result.value