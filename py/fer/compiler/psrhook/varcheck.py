from __future__ import absolute_import

from fer.ferutil import *
from fer.grammer import ParseResult
from .loader import RealmLoader


log = logger.get_logger()

class VariableAnalysis(object):

  def __init__(self, interceptor, parser_class):
    self.interceptor = interceptor
    self.parser_class = parser_class
    self.global_scope = {}
    self.current_scope = self.global_scope

    self.interceptor.register(parser_class.on_realm_domain_import, self.add_domain_id_import)
    self.interceptor.register(parser_class.on_domain_declaration_id, self.add_domain_id_partial)

  def add_domain_id_import(self, realm_import, nocontext):
    if realm_import:
      for d_import in realm_import.value.domains:
        d_name = d_import.domain if d_import.as_domain is None else d_import.as_domain
        if d_name in self.current_scope:
          return ParseResult(error="Can not redefine domain named : " + d_name,
              coord=d_import._fcrd)
        else:
          self.current_scope[d_name] = getattr(realm_import.value, RealmLoader.PARSED_IMPORTED_ATTR, None)
    return realm_import

  def add_domain_id_partial(self, id, nocontext):
    #if id in self.scope:

    #self.scope[id] = {}
    return id