#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/mask-slot-compile.pid
trap 'echo $? > evidence/mask-slot-compile.exit' EXIT
free -m > evidence/mask-slot-compile.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -30 >> evidence/mask-slot-compile.resources
available=$(awk '/MemAvailable:/{print $2}' /proc/meminfo)
if test "$available" -lt 120000000; then exit 2; fi
prlimit --as=2147483648 -- python3 compile-mask-slots.py > evidence/mask-slot-compile.log 2>&1
