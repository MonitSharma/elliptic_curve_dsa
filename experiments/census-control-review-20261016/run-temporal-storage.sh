#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/census-control-review-20261016
echo $$ >temporal-audit.pid
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -15; } >temporal-preflight.log
(ulimit -v 16777216;/usr/bin/time -v timeout -k 10 300 python3 temporal-storage.py) >temporal-audit.log 2>&1
code=$?;echo "$code" >temporal-audit.exit;exit "$code"
