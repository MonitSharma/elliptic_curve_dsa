# Pre-test review stopped the first representation prototype

The inline-constant XOR fast path omitted the term-bound check when adding a nonzero constant to a symbolic polynomial already at8terms. That only retained extra exact information, but did not match the declared unchanged8term policy. No native/input run or result exists. V2 restores the same bound on both constant-XOR branches and removes a tautological preparation assertion; quantum source/cache/fixtures unchanged.
