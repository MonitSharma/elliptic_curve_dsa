"""Inspect public exact edit syntax; no circuit edits or score claims."""
from pathlib import Path
import struct
import sys
data=Path(sys.argv[1]).read_bytes()
n=struct.unpack_from('<I',data)[0]
flat=4+12*n
print('edits',n)
shown=0
for i in range(n):
 at,start,count=struct.unpack_from('<III',data,4+12*i)
 rows=[struct.unpack_from('<6H',data,flat+12*(start+j)) for j in range(count)]
 if rows[0][0]==13:
  print('op',at,'records',count,'rows',rows[:14])
  shown+=1
  if shown==8:break
