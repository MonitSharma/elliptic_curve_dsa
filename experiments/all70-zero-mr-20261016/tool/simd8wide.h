#ifndef RESEARCH_SIMD8WIDE_H
#define RESEARCH_SIMD8WIDE_H
#include <stdint.h>
#include <stddef.h>
typedef struct { uint16_t a,b,t; uint8_t k,pad; uint32_t c,bt; } CompactOp;
/* Caller validates operands, stream balance, CPU AVX512 feature availability.
 * Rows q/bits/stack/rng have eight u64 words. All R/HMR consume one rng row.
 * Return 0 success; 1 short rng, 2 stack cap, 3 stack underflow, 4 bad opcode,
 * 5 unbalanced stack, 6 extra rng. used is always set on return. */
int simd8_run(const CompactOp *,size_t,uint64_t *,uint64_t *,uint64_t *,
 const uint64_t *,size_t,uint64_t *,size_t,size_t *);
#endif
