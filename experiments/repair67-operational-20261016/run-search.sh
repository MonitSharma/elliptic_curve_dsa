#!/bin/bash
set -euo pipefail
echo "DISABLED SOURCE PROPOSAL: no launch/build/search authority" >&2
exit 2
# After separate source review and acceptance, root must create a NEW reviewed
# revision that deliberately removes both this gate and coordinator's gate.
# Do not change or interrupt the existing product25 search.
