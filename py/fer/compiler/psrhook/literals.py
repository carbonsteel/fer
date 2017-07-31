from fer.grammer import ParseValue

def conv_float(f, nocontext):
  if f:
    return ParseValue(value=float((f.value.minus or '')+f.value.ipart+'.'+f.value.dpart),
        coord=f.coord, causes=f.causes)
  else:
    return f
def conv_int_b10(f, nocontext):
  if f:
    return ParseValue(value=int((f.value.minus or '')+f.value.ipart),
        coord=f.coord, causes=f.causes)
  else:
    return f

class Literals(object):
  def __init__(self, context):
    self.context = context
    self.context.interceptor.register(self.context.parser_class.on_integer_decimal,
        conv_int_b10)
    self.context.interceptor.register(self.context.parser_class.on_float,
        conv_float)