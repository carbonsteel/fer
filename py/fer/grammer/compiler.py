import datetime
import io
import json
import re

from fer.ferutil import *
from fer.grammer.common import *
from fer.grammer.grammar import *

KEY_FER_COORD = "_fcrd"
KEY_IMMEDIATE = "_fimm"

log = logger.get_logger()

def compile_parser(grammar_file, parser_module_name, parser_name):
  result = None
  log.info("Parsing grammar file")
  with io.open(grammar_file, "r", encoding='utf-8') as f:
    r = ParseReader(f, grammar_file)
    gp = GrammarParser(r)
    result = gp()
    if not result:
      log.error("Failed to parse grammar file")
    else:
      log.info("Parsed grammar file")
      with io.open(parser_module_name+".py", "w+") as f:
        gpc = GrammarParserCompiler(f, result, parser_name)
        gpc()
        f.flush()
        log.info("Wrote parser file")
  return (r.stats, result)

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
    synonym_maybe = False
    synonym_is_str = False
    for d in composite.expression:
      if d["anchor"] is None: # there was no anchor
        continue
      elif d["anchor"] == "": # there was one anchor -> the name is the id
        name = id_to_var(d["identifier"])
        members[name] = {}
      elif d["anchor"] == "@": # two anchors -> the value is bound to the parent
        name = id_to_def(d["identifier"])
        synonym_of = name
        synonym_unicity = d["quantifier"][0] == d["quantifier"][1] == 1
        synonym_maybe = d["quantifier"][0] == 0 and d["quantifier"][1] == 1
        try:
          synonym_is_str = type(self.known_definitions[d["identifier"]]) == GrammarClassDefinition
        except KeyError:
          raise ValueError("%s is used in %s but is not defined yet" % (d["identifier"], definition.id))
      else:
        name = d["anchor"]
        members[name] = {}
    W = self.get_writer()
    if len(members) > 0:
      members[KEY_FER_COORD] = {}
      members_keys = members.keys()
      W += "class {}(object):".format(id_to_def(definition.id))
      W += "  def __init__(self, {}):".format(", ".join(members_keys))
      for m_name in members_keys:
        W += "    self.{0} = {0}".format(m_name)
      W += "  def __pformat__(self, state):"
      W += "    pformat_class({}, self, state)".format(repr(sorted(members_keys)))
      return None
    elif synonym_of is None:
      W += "%s = str" % id_to_def(definition.id)
      return None
    else:
      if synonym_maybe:
        return "%s = idem" % id_to_def(definition.id)
      elif synonym_unicity:
        return "%s = %s" % (id_to_def(definition.id), id_to_def(synonym_of))
      elif synonym_is_str:
        return "%s = str" % id_to_def(definition.id)
      else:
        return "%s = list" % id_to_def(definition.id)

  def _w_parser_for_definition(self, definition, is_root):
    PARSER_FORMAT = "(%s, 'expected %s', self.%s)"
    is_immediate = False
    W = self.get_writer()
    literal = cclse = ccls = None
    if ofinstance(definition.value, GrammarClassDefinition):
      ccls = repr(definition.value.ccls.encode().decode('unicode_escape'))
      if definition.value.cclse is None:
        W += "  {} = SimpleClassPredicate.factory(r{})".format(id_to_predicate(definition.id), ccls)
      else:
        cclse = repr(definition.value.cclse.encode().decode('unicode_escape'))
        W += "  {} = FixedEscapedClassPredicate.factory(r{}, r{})".format(id_to_predicate(definition.id), ccls, cclse)
      W += "  def %s(self, imin=1, imax=1):" % id_to_parse(definition.id)
    elif ofinstance(definition.value, GrammarLiteralDefinition):
      literal = repr(definition.value.literal.encode().decode('unicode_escape'))
      W += "  {} = StringPredicate(r{})".format(id_to_predicate(definition.id), literal)
      W += "  def %s(self):" % id_to_parse(definition.id)
    else:
      W += "  def %s(self):" % id_to_parse(definition.id)
    W += "    value = self._reader.parse_type("
    W += "      result_type=%s," % id_to_def(definition.id)
    W += "      error='expected %s'," % definition.id
    W += "      parsers=["
    if ofinstance(definition.value, GrammarCompositeDefinition):
      composite = definition.value
      # coord record must be executed first so has to get the starting point
      # of whatever is being parsed. It must also not be added when there is
      # no anchor or an immediate
      qty_anchors = 0
      has_imm = False
      for e in composite.expression:
        if e["anchor"] is not None:
          qty_anchors += 1
        if e["anchor"] == "@":
          has_imm = True
          break
      if not(has_imm or qty_anchors == 0):
        W += "        (%s, 'built-in coord record', lambda: ParseValue(value=self._reader.get_coord(), coord=self._reader.get_coord()))," % repr(KEY_FER_COORD)
      for e in composite.expression:
        if e["identifier"] not in self.known_definitions:
          raise ValueError("%s is used but is not defined" % e["identifier"])
        anchor = None
        if e["anchor"] is None: # there was no anchor
          anchor = ""
        elif e["anchor"] == "": # there was one anchor -> the name is the id
          anchor = id_to_var(e["identifier"])
        elif e["anchor"] == "@": # two anchors -> the value is bound to the parent
          anchor = KEY_IMMEDIATE
          is_immediate = True
        else:
          anchor = id_to_var(e["anchor"]) # there was a named anchor -> use that as the id
        inner_parse = None
        if e["quantifier"][0] == e["quantifier"][1] == 1:
          inner_parse = "self." + id_to_parse(e["identifier"])
        elif type(self.known_definitions[e["identifier"]]) == GrammarClassDefinition:
          inner_parse = "lambda: self.%s(%d, %d)" % (
            id_to_parse(e["identifier"]), e["quantifier"][0], e["quantifier"][1]
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
      W += "        (%s, 'expected %s', lambda: self._reader.consume_string(self.%s, %d, %d))" % (
        repr(KEY_IMMEDIATE), definition.id, id_to_predicate(definition.id), len(literal)-2, len(literal)-2
      )
      is_immediate = True
    elif ofinstance(definition.value, GrammarClassDefinition):
      try:
        re.compile(ccls[1:-1])
      except re.error as e:
        raise ValueError('Invalid class in definition {}'.format(ccls)) from e
      if definition.value.cclse is None:
        W += "        (%s, 'expected %s', lambda: self._reader.consume_string(self.%s, imin, imax))" % (
          repr(KEY_IMMEDIATE), definition.id, id_to_predicate(definition.id)
        )
      else:
        cclse = repr(definition.value.cclse.encode().decode('unicode_escape'))
        try:
          re.compile(cclse[1:-1])
        except re.error as e:
          raise ValueError('Invalid class escape in definition {}'.format(cclse)) from e
        W += "        (%s, 'expected %s', lambda: self._reader.consume_string(self.%s, imin, imax))" % (
          repr(KEY_IMMEDIATE), definition.id, id_to_predicate(definition.id)
        )
      is_immediate = True
    elif ofinstance(definition.value, GrammarAlternativeDefinition):
      alts = ["self." + id_to_parse(alt) for alt in definition.value.alternative]
      W += "        (%s, 'expected %s', lambda: self._reader.parse_any([%s]))" % (
        repr(KEY_IMMEDIATE),
        "%s, any of %s" % (definition.id,", ".join(definition.value.alternative)),
        ",".join(alts)
      )
      is_immediate = True
    elif definition.value == "__whitespace__":
      W += "        ('', 'expected <whitespace>', lambda: self._reader.consume_string(WhitespacePredicate(), 0, {}))".format(sys.maxsize)
    else:
      raise ValueError("this should never happen (unless a new Grammar**Definition is added and not updated here)")
    if is_immediate:
      W += "      ],"
      W += "      result_immediate=%s)" % repr(KEY_IMMEDIATE)
    else:
      W += "      ])"
    if definition.hook is not None:
      W += "    value = self.interceptor.trigger(self.%s, value)" % (definition.hook,)
    W += "    return value"

  def __call__(self):
    W = self.get_writer()
    W += "# AUTOMATICLY GENERATED FILE."
    W += "# ALL CHANGES TO THIS FILE WILL BE DISCARDED."
    W += "# Updated on " + str(datetime.datetime.now())
    W += "from fer.grammer import *"
    W += "# Classes"
    synonyms = []
    hooks = []
    for g in self.grammar:
      if ofinstance(g.value, GrammarCompositeDefinition):
        synonym = self._w_class_for_composite_definition(g)
        first = False
        if synonym is not None:
          synonyms.append(synonym)
      elif ofinstance(g.value, GrammarAlternativeDefinition):
        W += "%s = idem" % id_to_def(g.id)
      else:
        W += "%s = str" % id_to_def(g.id)
      self.known_definitions[g.id] = g.value
      if g.hook is not None:
        hooks.append(g.hook)
    for s in synonyms:
      W += s
    
    W += "# Main parser"
    W += "class _ParserImpl(object):"
    counter = 0
    for hook in hooks:
      W += "  %s = %d" % (hook, counter)
      counter += 1
    W += "  def __init__(self, reader, interceptor):"
    W += "    self._reader = reader"
    W += "    self.interceptor = interceptor"
    W += "  def __call__(self):"
    W += "    return self.%s()" % id_to_parse(self.grammar[0].id)
    first = True
    for g in self.grammar:
      self._w_parser_for_definition(g, first)
      first = False
    W += "%s = _ParserImpl" % (self.parser_name)