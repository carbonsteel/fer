# fer language

# Realms

Fer code resides in `.fer` files. The scope of a file is refered to as a realm.

A `realm` may import domains from other realms using the `from` clause before any domain is defined locally.

# Domains

A `domain` defines a scope of possibilities that may be operated upon as well as transformations applied to domain instances. It consists of variables, subdomains and transforms.

```
domain Animal {
  | Zebra
  | Elephant
}
```

The domain Animal, above, defines two subdomains, Zebra, and Elephant.

## Subdomains 

Subdomains are equivalent to domains in every way but, they use `|` as prefix instead of `domain` in other to limit the propagation of syntaxic errors caused by unclosed curly braces. Unclosed domains or subdomains will cause an error at the next realm-level domain instead of at EOF if subdomains were to use the same `domain` prefix.

# Variables (and constants)

A domain may be parametrized using variables and may also define constants using any other variable available in its scope. Both must be declared using `.` (dot) followed by an identifer.

Variables may be left unbound, or bound to a domain or subdomain using `:` (colon).

Constant must be given a value using `~` (tilde).

```
domain V {
  . U          # unbound variable, it may be any domain or subdomain
  . a : Animal # bound variable, `a` may only be a direct subdomain of Animal, (either Zebra or Elephant)
  . c ~ a      # constant variable, `c` will be equivalent to `a`
}
```

## Subdomains

Subdomains of a parametrized domain are also parametrized with the same variables.

```
domain D {
  . x
  | E
}
```

In these invocations 1:`D(.x~Animal/Zebra)/E` and 2:`D(.x~Animal/Elephant)/E` subdomains `E` are not equivalent. Within `E` in the context of 1, `x` will be `Animal/Zebra` (Zebra of Animal) and in the context of 2, `x` will be `Animal/Elephant` (Elephant of Animal).

Note that `.` (dot) is a prefix used to name expressions.

Also note that in an expression, `/` (slash) is used like a path delimiter, for instance `Animal/Elephant` is reaching for `Elephant` inside `Animal`.

# Transforms

Any domain may also define transforms. If no transform is defined, the default behavior is to simply  return the domain itself.

Note that transforms are evaluated in the order they are defined.

## Codomains

A domain that does not explicitly specify a codomain has its codomain set to itself. Any invocation of such domain can only return that domain.

The following definitions are equivalent
```
domain T
```
```
domain T {
  >$ T
}
```

If a domain specifies a codomain, its transforms must return one of the codomain's direct subdomains.

```
domain A -> Animal {
  >$ Zebra
}
```

To retreive a domain specifing a codomain, use `&` (ampersand) before its name in an expression. `&A` returns `A` itself, while `A` will evaluate A's transforms and return `Zebra`.

## Compares

