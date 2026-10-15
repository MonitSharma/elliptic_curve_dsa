#ifndef MASK_SLOTS_H
#define MASK_SLOTS_H
#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t kind,a,b,dest; } SlotOp;
/* Load/admit only a plan whose every instruction/root was checked against the
 * frozen MRMASK01 source (verify-mask-slots.py). Slots may be overwritten; child
 * initialization/lifetime correctness is established by that complete check.
 * ports and out have8u64 per Boolean value. width=1..8 executes only leading
 * words. Workspace has capacity_words >= nslots*width u64 (packed width stride).
 * out is dependency upper bound: known=~out. Unused output words are zero.
 * Caller must mask unused words inactive; zero padding itself is not evidence.
 * Returns0 success;1 arguments;2 opcode;3 slot;4 port;5 capacity.
 */
int mask_slot_eval(const SlotOp*,size_t nops,size_t nslots,const uint64_t*ports,
 size_t nports,uint64_t*workspace,size_t capacity_words,const uint32_t*root_slots,
 size_t nroots,unsigned width,uint64_t*out);
#endif
