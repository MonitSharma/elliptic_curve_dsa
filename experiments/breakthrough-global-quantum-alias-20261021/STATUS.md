# Pre-test guarded-complement refinement

No native/full-stream scan ran. Review of the guarded-complement fixture showed that a wire equal to g*(1 XOR product) need not be the global complement of g*product outside g. V2 adds the exact expression flip XOR effective_guard to the complement lookup. This is an additional exact equality case, never an assumed implication. Original source/freeze preserved.
