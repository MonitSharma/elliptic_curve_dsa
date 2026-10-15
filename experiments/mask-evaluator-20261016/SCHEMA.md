# MRMASK01 input-conditioned dependency-mask DAG

Eight magic bytes MRMASK01, then three little-endian u64 values: node count,
input count1024, output count512. Follow with node_count16-byte records
(u32kind,a,b,aux), then512little-endian u32 output-root indices.

Kinds:0constantfalse,1constanttrue,2inputport(a),3XOR(a,b),4AND(a,b),5OR(a,b).
Every binary child precedes its node; aux is zero. Input ports are the declared
four256-bit registers P.x,P.y,A.x,A.y, in that order. Output roots correspond
to scored P.x/P.y bits. Roots are conservative dependency upper bounds;
knownness is their complement. Source/export/kernel hashes must be verified.
No opaque/fresh input terminal is accepted. No global RNG-independence claim
follows merely from evaluator correctness.

The C ABI stores each port/node/output value as eight little-endian u64 words,
with512independent inputs represented by its512bits. It validates every opcode,
child, port, root and buffer count before the relevant memory access.
