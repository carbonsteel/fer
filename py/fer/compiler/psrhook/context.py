from fer.grammer import InterceptorNotTrigerableSentinel

class CompilerContext(object):
  def __init__(self, interceptor, parser_class):
    self.interceptor = interceptor
    self.parser_class = parser_class
    self.on_before_parse_realm = InterceptorNotTrigerableSentinel
    self.on_compilation_done = InterceptorNotTrigerableSentinel