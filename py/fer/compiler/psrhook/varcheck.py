
from fer.ferutil import *
from fer.grammer import ParseResult

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
    #for domain_import in realm_import.domains:
    #  if id in self.current_scope:
    #    return ParseResult(error="Domain ")
    return realm_import

  def add_domain_id_partial(self, id, nocontext):
    #if id in self.scope:

    #self.scope[id] = {}
    return id