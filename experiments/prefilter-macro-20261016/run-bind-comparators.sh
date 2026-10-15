#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-macro-20261016
while [ ! -f compare-ends.exit ];do sleep 1;done
if [ "$(cat compare-ends.exit)" -ne 0 ];then exit 1;fi
{ hostname; date -Is; uptime; free -h; ps -eo pid,comm,nlwp,pcpu,rss,args --sort=-pcpu | head -20; } > preflight-comparator-bind.log
gcc -O3 -shared -fPIC anchor_scan.c -o anchor_scan.so > build-anchor.log 2>&1
code=$?;echo "$code" > build-anchor.exit
if [ "$code" -ne 0 ];then exit "$code";fi
/usr/bin/time -v python3 bind-comparators.py > bind-comparators.log 2>&1
echo "$?" > bind-comparators.exit
