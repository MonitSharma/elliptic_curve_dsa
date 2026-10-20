#!/bin/sh
set -eu
cd /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-sat-proof-tools-v2-20261020
test ! -e run.pid
nohup setsid sh run-local.sh > run.log 2>&1 < /dev/null &
printf '%s\n' "$!" > run.pid
cat run.pid
