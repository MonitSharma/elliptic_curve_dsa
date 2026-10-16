#include <stdint.h>
#include <stddef.h>
void normalize_bitids56(const uint64_t *in,uint64_t*out,size_t n){for(size_t i=0;i<n;i++){for(size_t j=0;j<7;j++)out[7*i+j]=in[7*i+j];out[7*i+4]=0;out[7*i+5]=0;}}
