#ifndef RESEARCH_SHAKE8_H
#define RESEARCH_SHAKE8_H
#include <stddef.h>
#include <stdint.h>
void *shake8_create(void);
void *shake8_clone(const void *);
void shake8_free(void *);
int shake8_absorb_same(void *,const unsigned char *,size_t);
int shake8_absorb8(void *,const unsigned char *,size_t,size_t);
int shake8_finalize(void *);
int shake8_squeeze8(void *,unsigned char *,size_t,size_t);
int shake8_words8(void *,uint64_t *,size_t);
int shake8_select_words8(void *,const size_t [8],uint64_t *,size_t);
#endif
