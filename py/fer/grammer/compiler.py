
import datetime

from fer.ferutil import *
from common import *
from grammar import *

class GrammarParserCompiler(object):
  def __init__(self, stream, parse_result, parser_name):
    if not parse_result:
      raise ValueError("innapropriate grammar")
    self._stream = stream
    self.grammar = parse_result.value
    self.parser_name = parser_name
    self.known_definitions = {}

  def get_writer(self):
    class _writer(object):
      def __init__(self, stream):
        self._stream = stream
      def __iadd__(self, b):
        self._stream.write(b)
        self._stream.write("\n")
        return self
    return _writer(self._stream)

  def _w_class_for_composite_definition(self, definition):
    if not ofinstance(definition.value, GrammarCompositeDefinition):
      raise ValueError("can't compile class for non composite definition")
    composite = definition.value
    members = {}
    synonym_of = None
    synonym_unicity = True
    synonym_is_str = False
    for d in composite.expression:
      if d["anchor"] is None: # there was no anchor
        continue
      elif d["anchor"] == "": # there was one anchor -> the name is the id
        name = kebab_to_snake(d["identifier"])
        members[name] = {}
      elif d["anchor"] == "@": # two anchors -> the value is bound to the parent
        name = kebab_to_camel(d["identifier"])
        synonym_of = name
        synonym_unicity = d["quantifier"][0] == d["quantifier"][1] == 1
        try:
          synonym_is_str = type(self.known_definitions[d["identifier"]]) == GrammarClassDefinition
        except KeyError:
          raise ValueError("%s is used in %s but is not defined yet" % (d["identifier"], definition.id))
      else:
        name = d["anchor"]
        members[name] = {}
    W = self.get_writer()
    if len(members) > 0:
      W += "class %s(object):" % id_to_def(definition.id)
      W += "  def __init__(self, **args):"
      W += "    StrictNamedArguments(%s)(self, args)" % repr(members)
    elif synonym_of is None:
      W += "%s = str" % id_to_def(definition.id)
    if synonym_of is not None:
      if synonym_unicity:
        return "%s = %s" % (id_to_def(definition.id), id_to_def(synonym_of))
      elif synonym_is_str:
        return "%s = str" % id_to_def(definition.id)
      else:
        return "%s = list" % id_to_def(definition.id)

  def _w_parser_for_definition(self, definition, is_root):
    PARSER_FORMAT = "(%s, 'expected %s', self.%s)"
    is_immediate = False
    W = self.get_writer()
    W += "  def %s(self):" % id_to_parse(definition.id)
    W += "    return self._reader.parse_type("
    W += "      result_type=%s," % id_to_def(definition.id)
    W += "      error='expected %s'," % definition.id
    W += "      parsers=["
    if ofinstance(definition.value, GrammarCompositeDefinition):
      composite = definition.value
      for e in composite.expression:
        if e["identifier"] not in self.known_definitions:
          raise ValueError("%s is used but is not defined" % e["identifier"])
        anchor = None
        if e["anchor"] is None: # there was no anchor
          anchor = ""
        elif e["anchor"] == "": # there was one anchor -> the name is the id
          anchor = kebab_to_snake(e["identifier"])
        elif e["anchor"] == "@": # two anchors -> the value is bound to the parent
          anchor = "_"
          is_immediate = True
        else:
          anchor = e["anchor"] # there was a named anchor -> use that as the id
        inner_parse = None
        if e["quantifier"][0] == e["quantifier"][1] == 1:
          inner_parse = "self." + id_to_parse(e["identifier"])
        elif type(self.known_definitions[e["identifier"]]) == GrammarClassDefinition:
          inner_parse = "lambda: self._reader.consume_string(SimpleClassPredicate(%s), %d, %d)" % (
            repr(self.known_definitions[e["identifier"]].ccls), e["quantifier"][0], e["quantifier"][1]
          )
        else:
          inner_parse = "lambda: self._reader.parse_many_wp(self.%s, %d, %d)" % (
            id_to_parse(e["identifier"]), e["quantifier"][0], e["quantifier"][1]
          )
        W += "        (%s, 'expected %s in %s', %s)," % (
          repr(anchor), e["identifier"], definition.id, inner_parse
        )
      if is_root:
        W += "        ('', 'expected eof', self._reader.consume_eof),"
    elif ofinstance(definition.value, GrammarLiteralDefinition):
      W += "        ('_', 'expected %s', lambda: self._reader.consume_string(StringPredicate(%s), %d, %d))" % (
        definition.id, repr(definition.value.literal), len(definition.value.literal), len(definition.value.literal)
      )
      is_immediate = True
    elif ofinstance(definition.value, GrammarClassDefinition):
      W += "        ('_', 'expected %s', lambda: self._reader.consume_string(SimpleClassPredicate(%s), 1, 1))" % (
        definition.id, repr(definition.value.ccls)
      )
      is_immediate = True
    else:
      raise ValueError("this should never happen (unless a new Grammar**Definition is added and not updated here)")
    if is_immediate:
      W += "      ],"
      W += "      result_immediate='_')"
    else:
      W += "      ])"

  def __call__(self):
    W = self.get_writer()
    W += "# AUTOMATICLY GENERATED FILE."
    W += "# ALL CHANGES TO THIS FILE WILL BE DISCARDED."
    W += "# Updated on " + str(datetime.datetime.now())
    W += "from fer.grammer import *"
    W += "# Classes"
    synonyms = []
    for g in self.grammar:
      if ofinstance(g.value, GrammarCompositeDefinition):
        synonym = self._w_class_for_composite_definition(g)
        first = False
        if synonym is not None:
          synonyms.append(synonym)
      else:
        W += "%s = str" % id_to_def(g.id)
      self.known_definitions[g.id] = g.value
    for s in synonyms:
      W += s
    
    W += "# Main parser"
    W += "class %s(object):" % id_to_parser(self.parser_name)
    W += "  def __init__(self, reader):"
    W += "    self._reader = reader"
    W += "  def __call__(self):"
    W += "    return self.%s()" % id_to_parse(self.grammar[0].id)
    first = True
    for g in self.grammar:
      self._w_parser_for_definition(g, first)
      first = False