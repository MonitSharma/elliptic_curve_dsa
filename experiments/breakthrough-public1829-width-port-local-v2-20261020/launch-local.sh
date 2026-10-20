#!/bin/sh
set -eu
cd /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-public1829-width-port-local-v2-20261020
test ! -e local-controller.pid
nohup setsid sh run-local.sh > local-controller.log 2>&1 < /dev/null &
printf '%s\n' "$!" > local-controller.pid
cat local-controller.pid
