#!/bin/bash
# PRODUCT179 phase A (unattended): wait for generation, freeze, universal certificate 96..179,
# native port with byte identity, then the declared gate. Stops on any failure; never searches or submits.
set -euo pipefail
ws=/home/hclau/ecdsa_research; px=$ws/product-exact-20261015; nd=$ws/product179-native-20261017
cd "$nd"; echo $$ > chain-a.pid
trap 'echo $? > '"$nd"'/chain-a.exit' EXIT
log() { echo "$(date -Is) $*" >> "$nd/chain-a.log"; }
log "waiting for stage 179"
while [ ! -e $px/product-to179-rank-20261017/launcher.exit ]; do sleep 60; done
test "$(cat $px/product-to179-rank-20261017/launcher.exit)" = 0
cd $px
[ -e PRODUCT179_FREEZE.json ] || python3 freeze179.py product > product179-freeze.log 2>&1
log "frozen: $(python3 -c "import json;print(json.load(open('PRODUCT179_FREEZE.json'))['external_stream_sha256'])")"
c=cache-certificate179-20261017
if [ ! -e $c/PLAN.json ]; then python3 extend_cache_certificate179.py prepare > $c.prepare.log 2>&1; fi
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
[ -e $c/RECEIPT.json ] || python3 extend_cache_certificate179.py run > $c/chain.log 2>&1
grep -q UNIVERSAL179_CHAIN_PASS $c/chain.log
[ -e $c/CACHE_EQUIVALENCE_CERTIFICATE.json ] || python3 consolidate_cache_certificate179.py > $c/consolidate.log 2>&1
[ -e $c/PER_INPUT_MASK_TRANSFER.json ] || python3 write_mask_transfer179.py > $c/mask-transfer.log 2>&1
[ -e PRODUCT179_ABI.json ] || python3 write_abi179.py > $c/abi.log 2>&1
log "certificate pass: $(cat $c/consolidate.log)"
cd "$nd"
bash run.sh
python3 -c "import json;d=json.load(open('NATIVE_IDENTITY.json'));assert d['status']=='NATIVE_BYTE_IDENTITY_PASS',d"
log "native identity pass"
bash gate-census.sh
log "gate: $(python3 -c "import json;g=json.load(open('GATE.json'));print(g['status'],g['failed_batches'],g['value_shots'],round(g['mcnemar_one_sided_p'],3),round(g['paired_mean_T_saving'],2),round(g['mean_T']['candidate'],2))")"
