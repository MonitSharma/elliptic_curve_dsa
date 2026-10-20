The v2 frozen source failed compilation before any test ran: its research
runtime selector scoped bit0 inside each G6 branch, while the unchanged following
free_bit(bit0) needs the common binding. Both branches now return that existing
BitId into let bit0. The original public arithmetic blocks are unchanged, both
still free their original internal bits, and the outer cleanup remains intact.
Earlier source/freezes/compiler failures remain untouched. No gate/nonce or
circuit verdict is re-run. The v1 empty-hunk parser failure also remains.
