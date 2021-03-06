import sys
import traceback

from .parser import ParseResultBase
from fer.ferutil import of, logger

log = logger.get_logger()

class InterceptorNotTrigerableSentinel(object):
  pass

class InterceptorError(Exception):
  pass

class Interceptor(object):
  CUSTOM_TRIGGERS = 0
  def __init__(self):
    self.calls = {}
  # triggers >= 0 are reserved for the parser compiler
  # triggers < 0 are for instance users
  def register_trigger(self):
    self.CUSTOM_TRIGGERS -= 1
    return self.CUSTOM_TRIGGERS
  def register(self, call_id, f, context=None):
    if call_id == InterceptorNotTrigerableSentinel:
      raise ValueError("Trigger has not been registered and will never fire")
    call = (f, context, traceback.format_stack())
    if call_id in self.calls:
      self.calls[call_id].append(call)
    else:
      self.calls[call_id] = [call]

  def trigger(self, call_id, value):
    if call_id not in self.calls:
      return value
    for f, context, reg_stack in self.calls[call_id]:
      try:
        value = of(ParseResultBase)(f(value, context))
      except TypeError as e:
        if str(e).startswith("expected value of type"):
          raise InterceptorError(
              "Interceptor expected ParseResult from callback callback registered at:\n"
              + "".join(reg_stack[:-1])) from e
        else:
          raise InterceptorError(
              "Interceptor could not call callback registered at:\n"
              + "".join(reg_stack[:-1])) from e
    return value  

# class Descriptor(object):
#   def __init__(self, interceptor, call_id):
#     self.interceptor = interceptor
#     self.call_id = call_id

#   def __call__(self, method):
#     def _DescriptorCallWrapper(*args, **kwargs):
#       value = method(*args, **kwargs)
#       return self.interceptor.trigger(self.call_id, value)
#     return _DescriptorCallWrapper

#   def __get__(self, instance, cls):           
#     return types.MethodType(self, instance, cls)
