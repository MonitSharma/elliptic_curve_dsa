#!/bin/sh
set -eu
cd /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-public1829-local-development-v2-20261020
test ! -e controller.pid
nohup setsid sh run-local.sh > controller.log 2>&1 < /dev/null &
printf '%s\n' "$!" > controller.pid
cat controller.pid
