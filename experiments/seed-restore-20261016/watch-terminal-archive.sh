#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/seed-restore-20261016
echo $$ > terminal-archive.pid
while [ ! -f qualification.exit ];do sleep 15;done
if [ "$(cat qualification.exit)" != 0 ];then echo 1 > terminal-archive.exit;exit 1;fi
python3 collect-terminal.py > terminal-archive.log 2>&1
code=$?
echo "$code" > terminal-archive.exit
exit "$code"
