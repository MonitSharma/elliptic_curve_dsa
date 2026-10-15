#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/mask-slot-validate.pid
trap 'echo $? > evidence/mask-slot-validate.exit' EXIT
free -m > evidence/mask-slot-validate.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -30 >> evidence/mask-slot-validate.resources
available=$(awk '/MemAvailable:/{print $2}' /proc/meminfo)
if test "$available" -lt 120000000; then exit 2; fi
gcc -O3 -march=native -fPIC -shared mask_slots.c -o libmask_slots.so > evidence/mask-slot-build.log 2>&1 || exit $?
prlimit --as=2147483648 -- python3 verify-mask-slots.py > evidence/mask-slot-verification.log 2>&1 || exit $?
prlimit --as=2147483648 -- python3 bench-mask-slots.py > evidence/mask-slot-runtime.log 2>&1 || exit $?
sha256sum mask_slots.c libmask_slots.so compile-mask-slots.py verify-mask-slots.py bench-mask-slots.py evidence/mr-mask-tip-v3-slots.bin evidence/mr-mask-tip-v3-slots.nodeids-u32le.bin evidence/mask-slot-verification.json evidence/mask-slot-runtime.json > evidence/mask-slot-validation.sha256
