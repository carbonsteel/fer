from fer.ferutil import *
from fer.grammer import ParseError
from .loader import RealmLoader


log = logger.get_logger()

class ScopeRoot(object):
  pass

class ScopePopError(Exception):
  pass

class ScopePushError(Exception):
  pass

class ScopeStack(object):
  def __init__(self, root):
    self._stack = [root]
  def __pformat__(self, state):
    pformat_class(['_stack'], self, state)
  def get_root(self):
    return self._stack[0]
  def push(self, key, scope):
    scope.parent = self.peek()
    scope.parent._push(key, scope)
    self._stack.append(scope)
  def peek(self):
    return self._stack[-1]
  def pop(self):
    if len(self._stack) < 2:
      return self._stack.pop()
    else:
      raise ScopePopError("Can not pop global scope!")

class GlobalScope(object):
  def __init__(self):
    self.parent = ScopeRoot
    self.realms = {}
  def __pformat__(self, state):
    pformat_class(['parent', 'realms'], self, state)
  # def _push(self, fullpath, realm):
  #   if isinstance(realm, RealmScope):
  #     self.realms[fullpath] = realm
  #   else:
  #     raise ScopePushError("GlobalScope can only contain realms, got {}."
  #         .format(type(realm).__name__))

class RealmScope(object):
  def __init__(self):
    self.parent = None
    self.declarations = {}
    self.domains = {}
  def __pformat__(self, state):
    pformat_class(['parent', 'declarations', 'domains'], self, state)
  # def _push(self, d_name, d):
  #   if isinstance(d, DomainScope):
  #     self.definitions[d_name] = d
  #   elif isinstance(d, RealmScope):
  #     self.declarations[d_name] = d
  #   else:
  #     raise ScopePushError("Unexpected type in RealmScope, got {}."
  #         .format(type(d).__name__))

class DomainScope(object):
  def __init__(self, parent=None):
    self.parent = parent
    self.variables = {}
    self.domains = {}
  def __pformat__(self, state):
    pformat_class(['parent', 'variables', 'domains'], self, state)
  # def _push(self, d_name, d):
  #   self.domains[d_name] = d

class VariableAnalysis(object):
  def __init__(self, context):
    self.context = context
    # self.scope_stack = ScopeStack(self._new_global_scope())
    self.realms = {}
    self.realm_stack = []

    self.context.interceptor.register(self.context.on_compilation_done,
        self._trace)
    self.context.interceptor.register(self.context.on_before_parse_realm,
        self.add_realm)
    self.context.interceptor.register(self.context.on_after_parse_realm,
        self.done_realm)

  def get_current_realm_scope(self):
    return self.realms[self.realm_stack[-1]]
  def get_parent_realm_scope(self):
    return self.realms[self.realm_stack[-2]]

  def _trace(self, result, nocontext):
    log.trace(logger.LazyFormat(spformat, self.realms))
    return result

  def _new_global_scope(self):
    return GlobalScope()
  def _new_realm_scope(self):
    return RealmScope()
  def _new_domain_scope(self, parent):
    return DomainScope()

  def add_realm(self, realm_import_result, nocontext):
    if realm_import_result:
      fullpath = getattr(realm_import_result.value, RealmLoader.LOADER_FULLPATH_ATTR, None)
      self.realms[fullpath] = self._new_realm_scope()
      self.realm_stack.append(fullpath)
    return realm_import_result

  def check_domain_declaration(self, parent_declaration, scope):
    # check definitions
    for domain_declaration in parent_declaration.domains:
      log.debug("Checking domain {}", domain_declaration.id)
      if domain_declaration.id in scope.domains:
        return ParseError(
            error="Declaration {} conflicting with another at {}".format(
                domain_declaration.id,
                scope.domains[domain_declaration.id]._fcrd),
            coord=domain_declaration._fcrd.levelup())
      else:
        # todo check codomain exists (need expressions)
        # remember domain exists
        scope.domains[domain_declaration.id] = domain_declaration
        domain_definition = domain_declaration.domain
        if domain_definition is None:
          # domain declaration OK
          continue
        else:
          domain_scope = DomainScope(scope)
          # todo check domain variables (need expressions)
          # recurse
          result = self.check_domain_declaration(domain_definition, domain_scope)
          if result is not None and not result:
            return result
          # todo check domain transforms (need expressions)
    return None

  def done_realm(self, realm_import_result, nocontext):
    try:
      if realm_import_result:
        realm = getattr(realm_import_result.value, RealmLoader.LOADER_IMPORTED_ATTR, None)
        # todo check imports
        result = self.check_domain_declaration(realm, self.get_current_realm_scope())
        if result is not None and not result:
          result.put(realm_import_result)
          return result
        for imp in realm_import_result.value.domains:
          if imp.domain not in self.get_current_realm_scope().domains:
            return ParseError(
                error="Import {} not found within realm {}".format(
                    imp.domain,
                    realm_import_result.value.realm),
                coord=imp._fcrd.levelup())
          else:
            d_name = imp.domain if imp.as_domain is None else imp.as_domain
            self.get_parent_realm_scope().domains[d_name] = self.get_current_realm_scope().domains[imp.domain]

      return realm_import_result
    finally:
      self.realm_stack.pop()

  def add_domain_id_import(self, realm_import_result, nocontext):
    """ Once loader.import_realm is over, check for import name conflicts and
         if imported domains are contained in the imported realm. """
    # if realm_import_result:
    #   for d_import in realm_import_result.value.domains:
    #     d_name = d_import.domain if d_import.as_domain is None else d_import.as_domain
    #     if d_name in self.get_current_realm_scope().domains:
    #       return ParseError(
    #           error="Import {} conflicting with another at {}".format(
    #               d_name, self.get_current_realm_scope().imports[d_name]._fcrd),
    #           coord=d_import._fcrd.levelup())
    #     else:
    #       realm = getattr(realm_import_result.value, self.LOADER_IMPORTED_ATTR, None)
    #       # log.trace(logger.Z(spformat, realm))
    #       for domain_declaration in realm.domains:
    #         if d_name == domain_declaration.id:
    #           self.get_current_realm_scope().domains[d_name] = domain_declaration
    #           break
    #       else:
    #         return ParseError(
    #             error="Import {} not in realm {}".format(d_name, realm_import_result.value.realm),
    #             coord=d_import._fcrd.levelup())
    #       self.get_current_realm_scope().imports[d_name] = d_import
    return realm_import_result
