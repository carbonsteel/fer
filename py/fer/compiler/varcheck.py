
from fer.grammer import ParseResult

class VariableAnalysis(object):
  def check_realm(self, realm):
    return ParseResult(error="Not implemented", coord=realm._fcrd)

def check_realm(realm):
  va = VariableAnalysis()
  return va.check_realm(realm)