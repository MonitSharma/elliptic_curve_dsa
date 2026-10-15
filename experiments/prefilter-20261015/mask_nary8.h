#ifndef MASK_NARY8_H
#define MASK_NARY8_H
#include <stdint.h>
#include <stddef.h>
typedef struct{uint32_t kind,a,b,packed;} NaryOp;
/* PERFORMANCE NEGATIVE: selected runtime remains MRSLOT02/libmask_fused.so.
 * MRSLOT03 header80bytes: magic8, rawMRMASK01 SHA25632, then u64LE
 * nops,nslots,ninputs,noutputs,npool. Instructions16bytes,512u32 roots,
 * then npool u32 packed operand pairs. Kinds0..14 are MRSLOT02.
 * Kind15 XOR: a=pooloffset,b=2..8terms,packed=dest. Each poolpair high16=65535,
 * low16=slotA. Kind16 SOP: same, each pair slotA16|slotB16<<16, where
 * slotB65535 denotes a linear term and other slotB denotes AND(slotA,slotB).
 * XOR all terms. Admit ONLY whole-plan source-reconstructed programs.
 * ports/out stride8u64; workspace packed width1..8; dependency output,
 * known=~out. Caller masks unused output words inactive.
 * fast variant additionally enforces first instruction CONST1->slot0 and
 * rejects every later slot0 overwrite, allowing branchless sentinel->slot0.
 */
int mask_nary8_eval(const NaryOp*,size_t,size_t,const uint64_t*,size_t,
 uint64_t*,size_t,const uint32_t*,size_t,unsigned,uint64_t*,const uint32_t*,size_t);
int mask_nary8_fast_eval(const NaryOp*,size_t,size_t,const uint64_t*,size_t,
 uint64_t*,size_t,const uint32_t*,size_t,unsigned,uint64_t*,const uint32_t*,size_t);
#endif
