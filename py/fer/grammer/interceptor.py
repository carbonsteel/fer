
class Interceptor(object):
  def __init__(self):
    self.calls = {}
  def register(self, call_id, f, context=None):
    if call_id in self.calls:
      self.calls[call_id].append((f,context))
    else:
      self.calls[call_id] = [(f,context)]

  def trigger(self, call_id, value):
    for f, context in self.calls[call_id]:
      value = f(value, context)
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
