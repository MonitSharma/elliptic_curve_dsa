"""Prepare only our factual README refresh while preserving another chat's notes."""
from pathlib import Path
import difflib,subprocess
r=Path(__file__).resolve().parents[2];readme=r/'README.md'
base=subprocess.check_output(['git','show','HEAD:README.md'],cwd=r).decode()
working=readme.read_text(encoding='utf-8')
def update(text):
    pairs=[
      ('**16 October 2026, 05:09 Singapore — product search is active.**','**16 October 2026, 06:09 Singapore — product search is active.**'),
      ('with no new product benchmark result yet.','with no new product benchmark result yet. The06:09 checkpoint records22.5million\ndistinct screened nonces without a pass.'),
      ('**16 October 2026, 01:45 Singapore — new complete local pass: 753,721\nToffolis at Q1468**, 50 below our public Toffoli record.','**16 October 2026, 06:08 Singapore — official Toffoli record: 753,721\nToffolis at Q1468**, 50 below our previous public Toffoli record.'),
      ('The earlier753,745/Q1464 complete pass remains a lower-width queued alternative.','The earlier753,745/Q1464 complete pass is preserved as a lower-width alternative;\nit no longer improves the current independent Toffoli minimum.'),
      ('**15 October 2026, 19:19 Singapore — our submission now has the lowest publicly\nscored Toffoli count: 753,771 at 1,464 qubits.**','**Historical result, 15 October 2026, 19:19 Singapore — our previous publicly\nscored Toffoli minimum: 753,771 at 1,464 qubits.**'),
      ('The next Toffoli target is **T ≤ 753,770**, at any allowed width. At our Q1464,\nthe strict product threshold is **T ≤ 641,631**.','The next Toffoli target is **T ≤ 753,720**, at any allowed width. At our Q1468,\nthe strict product threshold is **T ≤ 639,882**.'),
      ('Snapshot: **1,572 public submissions · 1,231 eligible scored records ·\n51 public Pareto points**, analyzed 16 October 2026 at 05:06 Singapore.\nThe new width minimum, Q677 (jackylee0424, `18912d63`), arrived after our\nToffoli submission.','Snapshot: **1,573 public submissions · 1,232 eligible scored records ·\n52 public Pareto points**, analyzed 16 October 2026 at06:08 Singapore.\nThe current width minimum is Q677 (jackylee0424, `18912d63`).'),
      ('local queued, stream`1d8c05ee`','officially scored as`03be8e19`, source`b5adb653`, stream`1d8c05ee`'),
      ('local queued, stream`ba9bd284`','complete local alternative, stream`ba9bd284`'),
      ('- **Toffoli reduction:** the two complete local passes above are queued.\n  Exact product-cache sources also pass native checks and fresh censuses, but\n  still need an affordable certified search and complete benchmark.','- **Toffoli reduction:** the753,721/Q1468 complete pass is now officially scored;\n  the753,745/Q1464 alternative is preserved. Product25 has an affordable\n  certified search running; product67 has native, fresh, universal and disabled\n  runtime qualification. Neither has a complete product benchmark result.'),
      ('- **Product record, measured on the public tip `4b2ec52f` (new):**','- **Historical exact-only search cost on public tip `4b2ec52f`:**'),
      ('  is therefore blocked until the failure rate drops to about 14 batches or\n  fewer, or a fast classical prefilter exists.','  was blocked under that exact-only cost model. The new certified prefilter\n  gives a measured19.609-hour mean projection at48threads on product25; this\n  is an expectation, not a completion guarantee. The search is now active.\n  [Current measured search](experiments/product25-operational-20261016/STATUS.md) ·\n  [New mask-cost figure and assumptions](experiments/search-cost-mask-20261016/STATUS.md).')]
    for old,new in pairs:
        assert text.count(old)==1,old[:90]
        text=text.replace(old,new)
    start=text.index('| **Minimum executed Toffolis** |');stop=text.index('\n',start)
    text=text[:start]+'| **Minimum executed Toffolis** | **753,721 at Q1468 — ours** | **Officially scored**; score-only product rejection | T ≤ 753,720 |'+text[stop:]
    old='1,048,576 fresh shots each. It is **queued, not officially submitted**, and\ndoes not improve the product record.'
    if old in text:
        text=text.replace(old,'1,048,576 fresh shots each. Official evaluation confirms these metrics as\n[`03be8e19`](https://api.ecdsa.fail/api/submissions/03be8e19-ab3b-45c7-9c62-9d78970c4d95),\nsource`b5adb653`. It is rejected solely because its product does not improve\nthe product record; it is the independent public Toffoli minimum.')
    else:
        old='Official validation is pending; it does not improve the product record.'
        assert text.count(old)==1
        text=text.replace(old,'Official evaluation confirms753,721/Q1468, source`b5adb653`; rejection is\nsolely because its product does not improve. It is the independent Toffoli minimum.')
    start=text.index('## Next work\n')
    tail=text[text.index('Only `src/point_add/` may change in a contestant submission.',start):]
    text=text[:start]+'''## Next work

1. **Finish a product record first.** The frozen product25 search is active.
   Preserve its source, ascending nonce ledger and disclosed fresh census;
   any pass must reproduce the unchanged full benchmark. Product67 is the
   stronger qualified alternative, with diagnostic savings documented in the
   [research report](experiments/product-exact-20261015/STATUS.md).
2. **Improve the official T753,721 record** (`03be8e19`, Q1468), aiming toward
   roughly753,670. Extra qubits are acceptable for this independent objective.
   Keep failed fresh gates separate; do not resample them or count source
   proxies as complete results.
3. **Reduce failures cheaply on the current product source.** Attribute the
   remaining current4b failures, qualify complete source-defined precision
   repairs, and prove fresh arithmetic-specific filters before combining them
   with exact caches. Earlier B3 witnesses are historical evidence.
4. Gate every frozen candidate with its predeclared fresh census and rate cap.
   Publish nonce, census and number screened. This run remainsqueue; separate
   user-authorized submissions are recorded explicitly.
5. **Width record:** the public minimum isQ677 (`d9d5e991`); the next target
   isQ676. Preserve the Q692 evidence and all failed experiments. Width is the
   third research priority, independent of the product and Toffoli records.
'''+ '\n' + tail
    return text
owned=update(base);updated=update(working)
folder=Path(__file__).resolve().parent
(folder/'README-owned-refresh.patch').write_bytes(''.join(difflib.unified_diff(base.splitlines(True),owned.splitlines(True),fromfile='a/README.md',tofile='b/README.md')).encode('utf-8'))
(folder/'README-owned-refresh.md').write_text(owned,encoding='utf-8')
assert '[Upload receipt and fresh verification]' in updated
readme.write_text(updated,encoding='utf-8')
print('Prepared owned-only indexed patch; working README retains other-chat upload note and link')
