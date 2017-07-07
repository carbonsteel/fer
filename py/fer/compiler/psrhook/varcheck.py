from __future__ import absolute_import

from fer.ferutil import *
from fer.grammer import ParseResult
from .loader import RealmLoader


log = logger.get_logger()

class VariableAnalysis(object):

  def __init__(self, context):
    self.context = context
    self.global_scope = self._new_scope()
    self.current_scope = self.global_scope

    self.context.interceptor.register(self.context.on_compilation_problem,
        self._trace)
    self.context.interceptor.register(self.context.on_before_parse_realm,
        self.add_realm)
    self.context.interceptor.register(self.context.parser_class.on_realm_domain_import,
        self.add_domain_id_import)
    self.context.interceptor.register(self.context.parser_class.on_domain_declaration_id,
        self.add_domain_id_partial)

  def _trace(self, result, nocontext):
    log.trace(logger.LazyFormat(repr, self.global_scope))
    return result

  def _new_scope(self):
    return {}

  def add_realm(self, realm_import_result, nocontext):
    if realm_import_result:
      fullpath = getattr(realm_import_result.value, RealmLoader.LOADER_FULLPATH_ATTR, None)
      self.global_scope[fullpath] = self._new_scope()
      self.current_scope = self.global_scope[fullpath]
    return realm_import_result

  def add_domain_id_import(self, realm_import, nocontext):
    if realm_import:
      for d_import in realm_import.value.domains:
        d_name = d_import.domain if d_import.as_domain is None else d_import.as_domain
        if d_name in self.current_scope:
          return ParseResult(
              error="Redifining domain {} from {}".format(
                  d_name, self.current_scope[d_name]._fcrd),
              coord=d_import._fcrd)
        else:
          self.current_scope[d_name] = getattr(realm_import.value, RealmLoader.LOADER_IMPORTED_ATTR, None)
    return realm_import

  def add_domain_id_partial(self, id, nocontext):
    #if id in self.scope:

    #self.scope[id] = {}
    return id