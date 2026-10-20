# Compilation stopped before native/input tests

Numeric cache exporter chained a slice iterator with owned Vec instead of its iterator. V2 fixes only that iterator argument; exact semantic/AIG/CNF logic unchanged. No source input or gate/nonce work ran.
