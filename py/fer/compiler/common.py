import sys

from fer.grammer import ParseCoord

class CompilerCoord(ParseCoord):
  def __init__(self, level=0):
    super().__init__(file="<compiler>", line=sys.maxsize, column=level)