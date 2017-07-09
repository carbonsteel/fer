from fer.ferutil import *
from fer.grammer import ParseResult
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
    self.__strict_named_attrs__ = ['_stack']
  def __pformat__(self, state):
    return autostr(self, state)
  def get_root(self):
    self._stack[0]
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
    self.__strict_named_attrs__ = ['parent', 'realms']
  def __pformat__(self, state):
    return autostr(self, state)
  def _push(self, fullpath, realm):
    if isinstance(realm, RealmScope):
      self.realms[fullpath] = realm
    else:
      raise ScopePushError("GlobalScope can only contain realms, got {}."
          .format(type(realm).__name__))

class RealmScope(object):
  def __init__(self):
    self.parent = None
    self.declarations = {}
    self.definitions = {}
    self.__strict_named_attrs__ = ['parent', 'declarations', 'definitions']
  def __pformat__(self, state):
    return autostr(self, state)
  def _push(self, d_name, d):
    if isinstance(realm, DomainScope):
      self.definitions[d_name] = d
    else:
      raise ScopePushError("RealmScope can only contain domains, got {}."
          .format(type(d).__name__))

class DomainScope(object):
  def __init__(self):
    self.parent = None
    self.variables = {}
    self.domains = {}
    self.__strict_named_attrs__ = ['parent', 'variables', 'domains']
  def __pformat__(self, state):
    return autostr(self, state)
  def _push(self, d_name, d):
    self.domains[d_name] = d

class VariableAnalysis(object):
  def __init__(self, context):
    self.context = context
    self.scope_stack = ScopeStack(self._new_global_scope())

    self.context.interceptor.register(self.context.on_compilation_problem,
        self._trace)
    self.context.interceptor.register(self.context.on_before_parse_realm,
        self.add_realm)
    self.context.interceptor.register(self.context.parser_class.on_realm_domain_import,
        self.add_domain_id_import)
    self.context.interceptor.register(self.context.parser_class.on_domain_declaration_id,
        self.add_domain_id_partial)

  def _trace(self, result, nocontext):
    log.trace(logger.LazyFormat(spformat, self.scope_stack))
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
      self.scope_stack.push(fullpath, self._new_realm_scope())
    return realm_import_result

  def add_domain_id_import(self, realm_import, nocontext):
    if realm_import:
      for d_import in realm_import.value.domains:
        d_name = d_import.domain if d_import.as_domain is None else d_import.as_domain
        if d_name in self.scope_stack.peek().declarations:
          return ParseResult(
              error="Import {} conflicting with another at {}".format(
                  d_name, self.scope_stack.peek().declaration[d_name]._fcrd),
              coord=d_import._fcrd)
        else:
          self.scope_stack.peek().declarations[d_name] = getattr(realm_import.value, RealmLoader.LOADER_IMPORTED_ATTR, None)
    return realm_import

  def add_domain_id_partial(self, id, nocontext):
    #if id in self.scope:

    #self.scope[id] = {}
    return id