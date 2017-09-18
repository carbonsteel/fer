# fer language (draft)

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

In these invocations 1:`D(.x~Animal/Zebra)/E` and 2:`D(.x~Animal/Elephant)/E` subdomains `E` are not equivalent. For `E` in the context of 1, `x` will be `Animal/Zebra` (Zebra of Animal) and in the context of 2, `x` will be `Animal/Elephant` (Elephant of Animal).

Note that `.` (dot) is a prefix assiated with named expressions.

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

Compares allow for any variable to be checked if its value is a given domain. The left-hand side of `=` (equal) must be a variable from the current scope and the right-hand side must be domain name, it must not be an expression.

```
domain Boolean {
  | False
  | True
}

domain not -> Boolean {
  . b : Boolean
  > .b=True $ False
  >$ True
}
```
Here, using the domain `Boolean`, the function `not` can be implemented with a domain transform where the variable `b` is compared to `Boolean/True` then negated if equal or else, if it is `False`, also negated.

### Why not an expression (This could be 100% wrong)

I want to compile transforms as jump tables in order to try to gain efficiency (trading speed for size) by avoiding conditionnal branchments and keep the CPU's pipeline full as much as possible.

By associating an index to a given domain, I think I could be able to compile a domain's transforms as a jump table with its index matching a truth table and thus evaluate all of its compares at once by only calculating the index from the variables. (Rephrase that dear god)

Example: (this is not how Natural would be compiled (see optimization goals), it just a convienient example)
```
# A natural number, 1: One, 2:Next(.n~One), 3:Next(.n~Next(.n~One)), etc.
domain Natural {
  | One
  | Next { . n:Natural }
}
domain NaturalMath {
  | sum -> Natural {
    . a:Natural
    . b:Natural

    # If a is One (case 1 and 2, b could be either One or Next, it does not matter)
    # then the sum is Next of b (1+b)
    > . a=One
    $ Next( . n~b )

    # If a is Next and b is One (case 2)
    # then the sum is Next of a (1+a)
    > . b=One
    $ Next( . n~a )

    # If a is not One and b is not One (case 4)
    # then the sum is Next of Next of sum of remainders (2+sum(a-1, b-1))
    >$ Next( . n~Next( . n~sum(
        . a~a/n
        . b~b/n
    )))
  }
```

Pseudo-code below

```
Natural = 0
NaturalMath = 1

NaturalBits = 1
One = 0
Next = 1
sum(a, b):
  i = (a << NaturalBits) + b
  return [
    # address of case 1,
    # address of case 2,
    # address of case 3,
    # address of case 4
  ][i]()

```

# Optimization goals
## Natural to integer
***(see the whiteboard snapshot)***

It may be possible to reduce domains to efficient equivalent
representations on the target hardware by analysing the meta properties of
domains and converting each domain component to an intermediate operation
that can then be converted to machine level instructions.

For the domain Natural:
```
domain Natural {
  | One
  | Next { .n~Natural }
}
```

