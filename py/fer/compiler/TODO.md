# todo

## Code generation
* Compute all individual possible code paths
 * Reorder transforms
 * Remove redundant transforms
 * Reduce remaining transforms
 * Reduce vars to final data structures
  * Ie recursive domains to depth tagged object, ie Natural to some integer
  * Recursive domains with other variables to sequences, to vectors
  * Prune unused domains
 * Generate function primitives: branch/jump-less instruction sequences
 * Sow primitives with appropriate jump tables or branch/jump
