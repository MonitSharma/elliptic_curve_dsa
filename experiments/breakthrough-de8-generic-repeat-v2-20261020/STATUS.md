# Setup stopped before tests or generation

The preserved point_add tree includes binary assets. UTF-8 alone cannot decode every source asset for a text patch. V3 compares original/current bytes first and only decodes changed Rust files; binary assets remain byte-identical. No input/gate/nonce work ran.
