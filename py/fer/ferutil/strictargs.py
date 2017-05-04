
from pformat import *

class StrictNamedArguments(object):
  def __init__(self, definitions, superdefinitions={}, hyperdefinitions={}):
    self._definitions = definitions
    self._superdefinitions = superdefinitions
    self._hyperdefinitions = hyperdefinitions
  @staticmethod
  def _is_required(meta):
    return "default" not in meta
  @staticmethod
  def _default(meta):
    return meta["default"]
  @staticmethod
  def _is_typed(meta):
    return "type" in meta
  @staticmethod
  def _type(meta):
    return meta["type"]
  def __call__(self, instance, args):
    all_definition_id = []
    definitions = self._definitions.copy()
    for id, meta in self._superdefinitions.iteritems():
      for a in meta["arguments"]:
        if a not in definitions:
          raise AttributeError("undefined argument %s in group %s" % (a, id))
      if meta["mutually_exclusive"]:
        found_one = None
        for x in meta["arguments"]:
          if x in args:
            if found_one is None:
              found_one = x
            else:
              raise AttributeError("unexpected argument %s, exclusivity already fullfilled for %s with argument %s" % (
                x, id, found_one
              ))
        if found_one is None:
          raise AttributeError("required exclusive group %s is missing an argument" % (id,))
        else:
          all_definition_id.append(id)
          setattr(instance, id, found_one)
          for x in meta["arguments"]:
            if x == found_one:
              continue
            del definitions[x]

    for id, meta in definitions.iteritems():
      if id not in args:
        if StrictNamedArguments._is_required(meta):
          raise AttributeError("required argument %s is missing" % (id,))
        else:
          all_definition_id.append(id)
          setattr(instance, id, StrictNamedArguments._default(meta))
          continue

      if StrictNamedArguments._is_typed(meta):
        try:
          all_definition_id.append(id)
          setattr(instance, id, StrictNamedArguments._type(meta)(args[id]))
        except (ValueError, TypeError) as e:
          raise GenericError("wrong type for argument %s, expected %s" % (
                  id, str(StrictNamedArguments._type(meta))), e)
      else:
        all_definition_id.append(id)
        setattr(instance, id, args[id])
    if "autostr" not in self._hyperdefinitions or self._hyperdefinitions["autostr"]:
      def autostr(instance, depth):
        attrs = []
        for id in instance.__strict_named_attrs__:
          attrs.append("%s=%s" % (str(id), pformat(getattr(instance, id), depth)))
        return """%s(%s)""" % (type(instance).__name__, ", ".join(attrs))
      setattr(instance, "__strict_named_attrs__", all_definition_id)
      setattr(type(instance), "__pformat__", autostr)