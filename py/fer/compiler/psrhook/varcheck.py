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
    #pformat_class(['parent', 'realms'], self, state)
    pformat_class(['realms'], self, state)
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
    #pformat_class(['parent', 'declarations', 'domains'], self, state)
    pformat_class(['declarations', 'domains'], self, state)
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
    #pformat_class(['parent', 'variables', 'domains'], self, state)
    pformat_class(['variables', 'domains'], self, state)
  # def _push(self, d_name, d):
  #   self.domains[d_name] = d

def expr_equals(a, b):
  """ return True if expression a is equivalent to expression b """
  if a.id != b.id or a.domainof != b.domainof:
    return False
  if a.arguments is None and b.arguments is None:
    pass
  elif (a.arguments is not None and b.arguments is not None
      and len(a.arguments) == len(b.arguments)):
    for i in range(0, len(a.arguments)):
      if a.arguments[i].id != b.arguments[i].id:
        return False
      if not expr_equals(a.arguments[i].expression, b.arguments[i].expression):
        return False
  else:
    return False
  if a.lookup is None and b.lookup is None:
    pass
  elif a.lookup is not None and b.lookup is not None:
    return expr_equals(a.lookup, b.lookup)
  else:
    return False
  return True

def expr_subdomain_of(a, b):
  """ return True if expression a is a subdomain of expression b
      expressions must be canonical
      ie:
        a = Boolean/True, b = Boolean, True
        a = True, b = Boolean, False
        a = Maybe(.v~Boolean)/Nothing, b = Maybe(.v~Boolean), True
        a = Maybe(.v~Boolean)/Nothing, b = Maybe(.v~Natural), False
  """
  # base case, previous lookup of b reach the end, so OK
  if b is None:
    return True
  # not handling literals yet
  if not(isinstance(a, self.context.parser_module.ExpressionCall) 
      and isinstance(b, self.context.parser_module.ExpressionCall)):
    return False
  # domains of the level cannot be subdomain of one another
  if a.lookup is None:
    return False
  # if the names match, we're on the right track
  if a.id == b.id:
    if len(a.arguments) != len(b.arguments):
      # Something freaky happened -- or is could it be from another realm?
      return False
    # check if arguments are the same
    for aarg, barg in zip(a.arguments, b.arguments):
      if not expr_equals(aarg, barg):
        return False
    return expr_subdomain_of(a.lookup, b.lookup)
  return False

def expr_canon(a_, scope, lookup_expr):
  """ return the canonical expression of expression a
      expressions a and lookup_expr must be valid
      returned expression is guaranteed to be valid within its context
      ie:
      1 d tautology -> Boolean {
          >$ True
        }
        The canonical expression of True 
          where scope is tautology 
                lookup_expr is Boolean 
          is Boolean/True
      2 d pure -> M {
          . x
          . X ~ &x
          . M ~ Maybe(.v~X)
          . J ~ Just(.v~x)
          >$ J
        }
        The canonical expression of J
          where scope is pure
                lookup_expr is M
          is Maybe(.v~&x)/Just(.v~x)
      3 d contradiction -> Natural {
          >$ Boolean/False
        }
        The canonical expression of Boolean/False
          where scope is contradiction
                lookup_expr is Natural
          is ParseError(...)
      4 >$ Maybe(.Value~Boolean)/Just(.v~True)
        The canonical expression of True
          where scope is <anything>
                lookup_expr is Maybe(.Value~Boolean)
          is Boolean/True
  """
  if a_ is None:
    return None
  if isinstance(a_, int) or isinstance(a_, float):
    return a_
  a = a_.value
  lookup_canon = expr_canon(lookup_expr, scope, None)
  return True
  scope_a_domain = scope.domain(a.id)
  if scope_a_domain:
    # if the valid expression a refers to a domain in scope
    #   it is already canonical
    # check if it matches the context
    if expr_subdomain_of(a, lookup_canon):
      return a
    else:
      return ParseError(error='Expression {} is not a subdomain of {} at {}'.format(
          a, lookup_canon, lookup_canon._fcrd), coord=a._fcrd.levelup())

  # todo everything else
  #return ParseError(error='Not implemented', coord=a._fcrd.levelup())
  return True

class VariableAnalysis(object):
  """ Step 1, on realm import, validate realm domains and canonicalize expressions
      Step 2, starting from Main domain resolve expressions usages, inline constants, 
  """
  def __init__(self, context):
    self.context = context
    root_realm = '<compiler>'
    self.realms = {root_realm: RealmScope()}
    self.realm_stack = [root_realm]
    self.checked_realms = set()

    self.context.interceptor.register(self.context.on_compilation_done,
        self._trace)
    self.context.interceptor.register(self.context.on_before_parse_realm,
        self.add_realm)
    self.context.interceptor.register(self.context.on_after_parse_realm,
        self.done_realm)

  def get_current_realm_scope(self):
    return self.realms[self.realm_stack[-1]]
  def get_current_realm_path(self):
    return self.realm_stack[-1]
  def get_parent_realm_scope(self):
    return self.realms[self.realm_stack[-2]]

  def _trace(self, result, nocontext):
    log.trace(logger.LazyFormat(spformat, self.realms))
    return result

  def add_realm(self, realm_import_result, nocontext):
    if realm_import_result:
      fullpath = getattr(realm_import_result.value, RealmLoader.LOADER_FULLPATH_ATTR, None)
      self.realms[fullpath] = RealmScope()
      self.realm_stack.append(fullpath)
    return realm_import_result

  def check_domain_arguments(self, expr, domain, scope):
    arguments = expr.arguments
    #log.trace(spformat(domain))
    variables = domain.variables
    if arguments is None:
      # the domain was not called with arguments
      if len(variables) > 0:
        # the domain has variables, and thus needs arguments, fail
        return ParseError(
            error="Domain '{}' used without arguments, needs: {}".format(expr.id,
              ", ".join(var for var in variables)),
            coord=expr._fcrd.levelup())
      else:
        # the domain has no variables, OK
        return True
    else:
      # the domain was called with arguments
      if len(variables) < 1:
        # the domain has no variables, it does not need them, fail
        return ParseError(
            error="Domain '{}' used with arguments, has no variables".format(expr.id),
            coord=expr._fcrd.levelup())
      else:
        # the domain has variables, check if they match arguments
        args = {}
        i = 0
        _vars = None
        if ofinstance(arguments, self.context.parser_module.ExpressionArgumentsOrdered):
          _vars = list(variables.values())
        for arg in arguments:
          if _vars is not None:
            arg.id = _vars[i].id
            i += 1

          if arg.id in args:
            return ParseError(
                error="Argument '{}' defined more than once at {}".format(arg.id,
                    arg._fcrd),
                coord=expr._fcrd.levelup())
          args[arg.id] = arg
          if arg.id in variables:
            # the argument is a variable
            if ofinstance(variables[arg.id], self.context.parser_module.VariableConstant):
              # an argument can not specify a value for a constant, fail
              return ParseError(
                  error="Argument '{}' overrides constant defined at {}".format(arg.id,
                      variables[arg.id]._fcrd),
                  coord=expr._fcrd.levelup())
            elif ofinstance(variables[arg.id], self.context.parser_module.VariableBound):
              # an argument must match the bound for its variable
              
              # check expression of argument
              argcheckresult = self.check_argument_value(arg.expression, scope, scope)
              if not argcheckresult:
                return argcheckresult
              # (type checking) check expression of argument is a subdomain of the variable's domain
              canoncheckresult = expr_canon(arg.expression, scope, variables[arg.id].variable_domain)
              if not canoncheckresult:
                return canoncheckresult
            continue
          else:
            # an argument must correspond to a variable
            return ParseError(
                error="Argument '{}' is not a variable in domain '{}'".format(arg.id,
                    expr.id),
                coord=expr._fcrd.levelup())
    return True

  def check_variable_domain(self, expr_, scope, lookup_scope):
    # [C11, C12] -> C13 
    return self._check_expr_callbacks(expr_, scope, lookup_scope, 
        lambda: True, # value may be a lambda (todo checks)
        lambda: ParseError(
            error="Bound may not be a literal",
            coord=expr_._fcrd.levelup()))
  def check_argument_value(self, expr_, scope, lookup_scope):
    return self._check_expr_callbacks(expr_, scope, lookup_scope, 
        lambda: True, # value may be a lambda (todo checks)
        lambda: True # value may be a literal(todo checks) 
    )

  def _check_expr_callbacks(self, expr_, scope, lookup_scope, on_lambda, on_literal):
    if ofinstance(expr_.value, self.context.parser_module.ExpressionCall):
      expr = expr_.value
      # check if usage succeeds definition
      # variables must come from the scope in which the expression resides
      #   this parameter must be (is always) the enclosing domain
      scope_var = scope.variable(expr.id)
      if not scope_var:
        # domains must come from within the scope of the domain being looked up
        #   this parameter varies during lookups
        scope_domain = lookup_scope.domain(expr.id)
        if not scope_domain:
          return ParseError(
              error="Expression identifier '{}' is not defined".format(expr.id),
              coord=expr._fcrd.levelup())
        else:
          # check if arguments match using the domain's variables
          argcheckresult = self.check_domain_arguments(expr, scope_domain, scope)
          if not argcheckresult:
            return argcheckresult
          if expr.lookup is None:
            # there is no lookup, nothing else to check
            return True
          else:
            # check if lookup in current domain
            if expr.lookup.value.id not in scope_domain.domains:
              return ParseError(
                  error="Expression lookup '{}' is not a subdomain of '{}'".format(
                    expr.lookup.value.id, expr.id),
                  coord=expr._fcrd.levelup())
            return self.check_variable_domain(expr.lookup.value, scope, scope_domain)
      else:
        # variable is defined
        # todo (type checking) check if its lookup is a subdomain of its value
        return True
    elif ofinstance(expr_.value, self.context.parser_module.ExpressionLambda):
      return on_lambda()
    else:
      return on_literal()
    # bound OK
    return True

  def check_domain_variables(self, domain, scope):
    # [C5] -> C9 check all domain variables
    for var in domain.variables:
      # C10 check variable id conflict
      scope_var = scope.variable(var.id)
      if scope_var:
        # C10E1 at least two variables share the same identifier, error
        return ParseError(
            error="Variable '{}' already defined at {}".format(
                var.id, scope_var._fcrd),
            coord=var._fcrd.levelup())
      else:
        # variable id is so far unique, remember it
        scope.variables[var.id] = var
      
      # boohoo polymorphism...
      if ofinstance(var, self.context.parser_module.VariableBound):
        # var is a boundable variable 
        if var.expression is not None:
          # C11 check bound variable domain
          result = self.check_variable_domain(var.expression, scope, scope)
          if not result:
            return result
        else:
          # var is unbounded, ok
          continue
      elif ofinstance(var, self.context.parser_module.VariableConstant):
        # var is a constant
        # C12 check constant expression
        result = self.check_variable_domain(var.expression, scope, scope)
        if not result:
          return result
        # constant ok
        continue

    return True

  def check_domain_declaration(self, parent_declaration, scope):
    # [C1] -> C3 check inner domains
    for domain_declaration in parent_declaration.domains:
      log.debug("Checking domain {}", domain_declaration.id)
      scope_domain = scope.domain(domain_declaration.id)
      if scope_domain:
        # C3E1 At least two inner domains share the same id, error
        return ParseError(
            error="Declaration '{}' conflicting with another at {}".format(
                domain_declaration.id,
                scope_domain._fcrd),
            coord=domain_declaration._fcrd.levelup())
      else:
        # The domain id is unique so far, remember domain exists
        domain_scope = DomainScope(scope)
        scope.domains[domain_declaration.id] = domain_scope
        # C4 Check inner domain definition
        domain_definition = domain_declaration.domain
        if domain_definition is None:
          if domain_declaration.codomain is not None:
            # C4E1 Inner domain is named with a codomain, codomains can only be used with transforms, error
            return ParseError(
                error="Declaration '{}' specifies a codomain without defining a domain".format(
                    domain_declaration.id),
                coord=domain_declaration._fcrd.levelup())
          else:
            # Inner domain is only named, OK
            continue
        else:
          # C5 check domain variables
          result = self.check_domain_variables(domain_definition, domain_scope)
          if not result:
            return result
          # C6 check codomain
          if domain_declaration.codomain is not None:
            result = self.check_variable_domain(domain_declaration.codomain, domain_scope, domain_scope)
            if not result:
              return result
          # C7 recurse, check inner inner domains
          result = self.check_domain_declaration(domain_definition, domain_scope)
          if not result:
            return result
          # todo C8 check domain transforms (need codomain)
    return True
  
  def done_realm(self, realm_import_result, nocontext):
    try:
      if realm_import_result:
        # don't re validate already loaded realms
        if self.get_current_realm_path() in self.checked_realms:
          return realm_import_result
        realm = getattr(realm_import_result.value, RealmLoader.LOADER_IMPORTED_ATTR, None)
        # C1 check domains in realm
        result = self.check_domain_declaration(realm, self.get_current_realm_scope())
        if not result:
          result.causes.append(realm_import_result)
          return result
        # C2 check imported domains from realm
        for imp in realm_import_result.value.domains:
          if imp.domain not in self.get_current_realm_scope().domains:
            # C2E1 the imported domain does not exist, error
            return ParseError(
                error="Import '{}' not found within realm '{}'".format(
                    imp.domain,
                    realm_import_result.value.realm),
                coord=imp._fcrd.levelup())
          else:
            # the imported domain exists, add it to the scope of the importer
            d_name = imp.domain if imp.as_domain is None else imp.as_domain
            self.get_parent_realm_scope().domains[d_name] = self.get_current_realm_scope().domains[imp.domain]
        # realm OK, remember it
        self.checked_realms.add(self.get_current_realm_path())
      return realm_import_result
    finally:
      self.realm_stack.pop()