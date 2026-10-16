#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/current-value-attribution-20261016
echo $$ >map.pid
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -18; } >map-preflight.log
/usr/bin/time -v python3 map-final-markers.py >map.log 2>&1
code=$?;echo "$code" >map.exit
exit "$code"
