# todo

## Compiler steps
1. Parse source file - Done
1. 1. Add imports - Done
1. 1. Look at adding decorators to parser methods to to inline semantics - Done
1. Verify variable semantics
1. 1. No domain overrides another within the same scope - Done
1. 1. Codomains are valid expressions
1. 1. Variables bounds are valid expressions
1. Find code paths
1. Verify domain transform semantics
1. Apply constant contraints and arguments
1. Map variables to primitive types and operations
1. Map transforms to primitive operations
1. Reduce transforms by merging equivalent operations
1. Translate primitives to instructions