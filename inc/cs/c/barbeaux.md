Memory allocation problem

* don't want to use any foreign dependencies (libc, etc.)
* don't want to worry about memory fragmentation (don't want to have that problem)

It seems to me that memory allocation is a dependency problem in which any node must have the least dependencies as possible. Nodes are instructions, dependencies are main memory addresses and registers.

Examples, where f is a function and no properties can be inferred from f and no f', inverse of f, exists:

    ; best case (tail call)
    -> a, b=f(a), c=f(b) : 3 dep
    ~> a, a=f(a), a=f(a) : 1 dep
    
    -> a, b, c=f(a,b), d=f(a,c) : 4
    ~> a, b, b=f(a,b), d=f(a,b) : 3
    
    ; worst case
    -> a, b=f(a), c=f(a,b), d=f(a,b,c), ... : inf
    
