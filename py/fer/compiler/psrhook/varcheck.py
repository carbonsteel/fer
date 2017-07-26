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
  def domain(self, domain):
    if domain in self.domains:
      return self.domains[domain]
    elif self.parent is not None:
      return self.parent.domain(domain)
    return None
  def variable(self, var):
    return None
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
  def domain(self, domain):
    if domain in self.domains:
      return self.domains[domain]
    elif self.parent is not None:
      return self.parent.domain(domain)
    return None
  def variable(self, var):
    if var in self.variables:
      return self.variables[var]
    elif self.parent is not None:
      return self.parent.variable(var)
    return None
  def __pformat__(self, state):
    pformat_class(['parent', 'variables', 'domains'], self, state)
  # def _push(self, d_name, d):
  #   self.domains[d_name] = d

class ZipDictStrictError(Exception):
  pass

def zipDictStrict(*dicts):
  base = dicts[0].keys()
  for d in dicts[1:]:
    if base != d.keys():
      raise ZipDictStrictError('All dicts must have the same keys.')
  for k in base:
    yield tuple(v for v in dicts[k])

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

  def check_domain_expression_arguments(self, expr, domain, scope):
    arguments = expr.arguments
    #log.trace(spformat(domain))
    variables = domain.variables
    if arguments is None:
      # the domain was not called with arguments
      if len(variables) > 0:
        # the domain has variables, and thus needs arguments
        return ParseError(
            error="Domain {} used without arguments, needs: {}".format(expr.id,
              ", ".join([var.id for var in variables])),
            coord=expr._fcrd.levelup())
      else:
        # the domain has no variables, OK
        return True
    else:
      # the domain was called with arguments
      if len(variables) < 1:
        # the domain has no variables, it does not need them
        return ParseError(
            error="Domain {} used with arguments, has no variables".format(expr.id),
            coord=expr._fcrd.levelup())
      else:
        # the domain has variables, check if they match arguments
        args = {}
        for arg in arguments:
          args[arg.id] = arg
          if arg.id in variables:
            # the argument is a variable
            if ofinstance(variables[arg.id], self.context.parser_module.VariableConstant):
              # an argument can not specify a value for a constant
              return ParseError(
                  error="Argument {} used with a constant from {}".format(arg.id,
                      variables[arg.id]._fcrd),
                  coord=expr._fcrd.levelup())
            elif ofinstance(variables[arg.id], self.context.parser_module.VariableBound):
              # an argument must match the bound for its variable
              # todo
              #result = self.check_expression()
              pass
          else:
            # an argument must correspond to a variable
            return ParseError(
                error="Argument {} is not a variable in domain {}".format(arg.id,
                    expr.id),
                coord=expr._fcrd.levelup())
    return True

  def check_expression(self, expr, scope):
    # check if usage succeeds definition
    scope_var = scope.variable(expr.id)
    if not scope_var:
      scope_domain = scope.domain(expr.id)
      if not scope_domain:
        return ParseError(
            error="Expression identifier {} is not defined".format(expr.id),
            coord=expr._fcrd.levelup())
      else:
        # check if arguments match using the domain's variables
        argcheckresult = self.check_domain_expression_arguments(expr, scope_domain, scope)
        if not argcheckresult:
          return argcheckresult
        if expr.lookup is not None:
          # todo check if lookup in domain
          return self.check_expression(expr.lookup, scope)
    else:
      # check if arguments match after resolving the variable bounds
      pass
    return True

  def check_domain_variables(self, domain, scope):
    for var in domain.variables:
      scope_var = scope.variable(var.id)
      if scope_var:
        return ParseError(
            error="Variable {} already defined at {}".format(
                var.id, scope_var._fcrd),
            coord=var._fcrd.levelup())
      else:
        scope.variables[var.id] = var
      # boohoo polymorphism
      if ofinstance(var, self.context.parser_module.VariableBound):
        if var.variable_domain is not None:
          result = self.check_expression(var.variable_domain, scope)
          if not result:
            return result
        if var.variable_constraints is not None:
          pass
        # variable OK
        continue
      elif ofinstance(var, self.context.parser_module.VariableConstant):
        # todo
        pass

    return True


  def check_domain_declaration(self, parent_declaration, scope):
    # check definitions
    for domain_declaration in parent_declaration.domains:
      log.debug("Checking domain {}", domain_declaration.id)
      scope_domain = scope.domain(domain_declaration.id)
      if scope_domain:
        return ParseError(
            error="Declaration {} conflicting with another at {}".format(
                domain_declaration.id,
                scope_domain._fcrd),
            coord=domain_declaration._fcrd.levelup())
      else:
        # todo check codomain exists (need expressions)
        # remember domain exists
        domain_scope = DomainScope(scope)
        scope.domains[domain_declaration.id] = domain_scope
        domain_definition = domain_declaration.domain
        if domain_definition is None:
          # domain OK
          continue
        else:
          # check domain variables
          result = self.check_domain_variables(domain_definition, domain_scope)
          if not result:
            return result
          # recurse, check sub domains
          result = self.check_domain_declaration(domain_definition, domain_scope)
          if not result:
            return result
          # todo check domain transforms (need expressions)
    return True

  def done_realm(self, realm_import_result, nocontext):
    try:
      if realm_import_result:
        realm = getattr(realm_import_result.value, RealmLoader.LOADER_IMPORTED_ATTR, None)
        # checking domains in realm
        result = self.check_domain_declaration(realm, self.get_current_realm_scope())
        if not result:
          result.put(realm_import_result)
          return result
        # checking imported domain from realm
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
        # realm OK
      return realm_import_result
    finally:
      self.realm_stack.pop()