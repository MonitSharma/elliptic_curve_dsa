#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/value-carry-contracts-20261016
echo $$ > terminal-analysis.pid
{ hostname; date -Is; free -h; ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -16; } >terminal-analysis-preflight.log
/usr/bin/time -v python3 analyze-terminals.py >terminal-analysis.log 2>&1
code=$?;echo "$code" > terminal-analysis.exit
exit "$code"
