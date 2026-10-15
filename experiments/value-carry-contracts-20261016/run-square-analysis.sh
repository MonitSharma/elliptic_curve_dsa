#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/value-carry-contracts-20261016
echo $$ > square-analysis.pid
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -16; } >square-analysis-preflight.log
/usr/bin/time -v python3 analyze-square.py >square-analysis.log 2>&1
code=$?;echo "$code" >square-analysis.exit
exit "$code"
