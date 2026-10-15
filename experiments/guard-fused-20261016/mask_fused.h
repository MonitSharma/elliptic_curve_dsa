#ifndef MASK_FUSED_H
#define MASK_FUSED_H
#include <stdint.h>
#include <stddef.h>
typedef struct{uint32_t kind,a,b,packed;} FusedOp;
/* MRSLOT02: 72-byte header = magic8, rawsourceSHA25632, then u64LE
 * nops,nslots,ninputs,noutputs. Then16-byte FusedOp records,512u32 root slots.
 * kinds0..5 retain CONST0,CONST1,INPUT,XOR,AND,OR. packed=destination slot.
 * kinds6..14 fuse child(parent operands a,b) into a third input c:
 * childkind=3+(kind-6)/3,parentkind=3+(kind-6)%3,
 * result=parentop(childop(slot[a],slot[b]),slot[c]).
 * packed=(c<<16)|destination. nslots<65536 is mandatory.
 * Admit ONLY plans with sourcehash binding and whole-plan independent check
 * verify-mask-fused.py against exact MRMASK01 and original-node-ID sidecar.
 * ports/out have8u64 stride; workspace packed stride width (1..8).
 * workspace capacity_words>=nslots*width. out gives DEPENDENCE upper bounds,
 * known=~out. Unused output words are zero; caller masks them inactive.
 * Returns0 success;1 args;2 opcode;3 slot;4 port;5 workspace capacity.
 */
int mask_fused_eval(const FusedOp*,size_t nops,size_t nslots,const uint64_t*ports,
 size_t nports,uint64_t*workspace,size_t capacity_words,const uint32_t*root_slots,
 size_t nroots,unsigned width,uint64_t*out);
#endif
