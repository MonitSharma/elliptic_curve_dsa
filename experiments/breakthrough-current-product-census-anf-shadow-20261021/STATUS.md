# Compile-only failure preserved

Rust could not infer the parsed scalar type inside assert_eq. No native test, point replay, census gate or nonce screen ran. V2 uses a generic scalar parser with the expected scalar argument determining the exact type; parse failures still panic. Original frozen source and compile logs are preserved. ANF/cache/source unchanged.
