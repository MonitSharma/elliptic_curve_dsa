#ifndef RESEARCH_RAIL8_H
#define RESEARCH_RAIL8_H
#include <stdint.h>
#include <stddef.h>
typedef struct {uint32_t w,n0,n1,n2,nb,anchor;} RailStep;
/* Advisory ONLY. Never a rejection certificate. Input is count AoS records,
 * each d1[4] then d2[4], little-endian limbs, canonical modulo secp256k1 p.
 * Flags bit0=nonunit, bit1=observed rail overflow. Source-bound step table. */
int rail8_population(const RailStep *steps,size_t nsteps,const uint64_t *pairs,
 size_t count,uint8_t *flags);
#endif
