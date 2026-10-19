"""Add this carry-research checkpoint while preserving all user document edits."""
import difflib,subprocess
from datetime import datetime,timezone,timedelta
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent
stamp=datetime.now(timezone.utc);sgt=stamp.astimezone(timezone(timedelta(hours=8))).strftime('%d %B %Y, %H:%M SGT')
reports={
'breakthrough-parity-bridge-20261020':'''# Source-exclusive parity carry bridge

Three native component tests pass. A source pivot may temporarily hold a
Cuccaro carry only if it occurs in exactly one addend row and aliases neither
target nor incoming carry. Its parity basis is restored exactly. Each borrowed
stage trades one extra emitted CCX for one fewer owned carry wire.

523776 small-basis evaluations n3..7 pass value/source/ancilla/phase checks
(some bridge patterns duplicate). Every physical RNG phase coefficient and
the inverse pass on64 bases. Unsafe source/target/carry aliases reject before
emitting gates. Four local Boolean lemmas are UNSAT; missing-CZ control SAT.
These local lemmas and written induction do not formally verify Rust control
flow or complete point addition. Protected17 unchanged. All23 archive members
verify locally. This is a component, not a point-add resource record.
''',
'breakthrough-parity-sites-20261020':'''# Source-exclusive carry availability on the accepted circuit

Byte-identical raw13f6 stream and protected17 checked. The observer records
946 carry ladders:402 plain and544 paused. There are394 plain sites with
source pivots and no pending carry hook. The first Q1234 peak lies inside a
136-bit plain ladder:1100 pre-existing wires,134 clean carries,133 available
source-exclusive pivot positions. This is availability, not a width result.

Paused callbacks can read source values or carry views modified by borrowing;
they need an explicit read/restoration contract. Plain-ladder source availability
does not license changing them. All22 archive members verify locally.
''',
'breakthrough-parity-integration-20261020':'''# Fixed1200 plain-ladder integration diagnostic

No product improvement. The frozen raw integration uses191 replacements and
5834 borrowed stages, but the global peak stays1234 and moves into a paused
ladder plus its comparison logic. Builder/generated counts are diagnostic.

Paired512x64 label breakthrough-parity-integration-raw-v1: exactly the same52
value-failing shot identities in both sources, zero dirty shots. Parent/candidate
phase shots38/43 and failed batches62/61. Candidate mean executed raw Toffolis
increase5109.21 (paired SE4.30). Eight full protected scalar controls per source
pass. These include failed inputs and are not a final gate or scored result.
No final census or nonce search. Protected17 unchanged; all40 archive members
verify locally. The accepted circuit remains unchanged.
''',
'breakthrough-parity-cap-20261020':'''# Exact source borrowing before rail splits: capacity admission

Negative whole-width admission result. Disabled cap1234 reproduces the exact
13f6 raw control. Enabled cap1234 generates at peak1234 with extra arithmetic.
All predeclared lower caps1233/1230/1226/1224/1200 fail native generation in
the Y15 fixed fold-storage planner. At1233, forward tick130 needs one more
wire than its existing shed/drop schedule permits. Generated counts are not
scores. No statistical gate or nonce ran. Protected17 unchanged; all47 archive
members verify locally. This motivates exact fold schedule work, not cuts.
''',
'breakthrough-parity-paused-20261020':'''# Paused parity ladder with an explicit consumer contract

Three native component tests pass. The callback may read original targets and
sources only from declared protected sets and only exposed carry views. It
must restore every source/target/carry value it touches. Borrowed MAJ stages
modify their incoming carry, so those views are explicitly unavailable.

261888 small-basis evaluations n3..7 pass a nontrivial intended-phase consumer
of protected sum parity (some bridge patterns duplicate). Every physical RNG
phase coefficient passes on64 bases. Read conflicts reject before emission.
The initial test API compile failure is preserved: repair-v2 spells Z as the
supported CZ(q,q), changing no runtime arithmetic bytes. Protected17 unchanged;
all35 archive members verify locally. No GCD callback integration or score.
''',
'breakthrough-fold-plan7-20261020':'''# Exact seven-carry schedule for the existing fifty-bit fold ladder

Native component success; no complete resource improvement yet. Chunks
[7,6,6,5,5,4,4,3,3,2,2,3] drop nonadjacent boundaries[0,2,4,6,8]. The existing
ladder_drop algorithm handles them without arithmetic-window or iteration
changes.65536 common affine inputs per old/new plan pass value, phase and
ancilla checks. Actual carry peaks8/7, emitted component CCX113/130. Invalid
adjacent drops reject as expected. These are component/static counts, not
scored point-add metrics or exhaustive physical-RNG coverage.

Raw cap1234 exactly reproduces13f6. Configured cap1233 generates, but its actual
global peak is1237 in square; raw builder expected cost762948.5. Caps1232/1230
fail other fixed fold-storage sites. A configured cap is not a measured width.
Protected17 unchanged; all39 archived members verify locally. The next isolated
study keeps the original square planning and borrows its carry source pivots.
''',
'breakthrough-fold-square-20261020':'''# Fold-plan7 with source borrowing in the square

In progress under server supervisor2361166. Exact plan7 walk, accepted1234
square chunk planner and boundaries, separate hard global carry cap. The
square's direct chunk routines borrow source-exclusive parity pivots only
when their clean carries exceed that cap. Native tests include arbitrary
carryout-target extension and the earlier parity/plan controls.

Predeclared capacities1234/1233;1234 must exactly reproduce13f6. Check run.exit
and ADMISSION-RESULT.json before continuing. A native generated count or a
configured cap is not a scored result. No final gate or nonce search declared.
'''}
for name,body in reports.items():(root/'experiments'/name/'STATUS.md').write_text(body,encoding='utf8',newline='\n')
prefix=f'''## {sgt}: exact carry borrowing and seven-carry fold

No new complete resource record or final gate. Official d9ae2845 remains the
accepted parent Q1234/T761077/product939169018. All historical verdicts stand.

Source-exclusive parity carry borrowing passes3 native tests and four local
Boolean lemmas; a paused variant with explicit consumer read/restoration
contract passes3 tests. Byte-identical source audit finds133 borrowable carry
positions at the first peak. Raw plain-only integration preserves the same52
value-failing shot identities and zero dirty shots on512 paired batches, but
keeps globalQ1234 and adds5109 diagnostic T. The peak moves into paused logic.
It is not a product improvement. Lower raw source-borrowing caps all fail the
Y15 fixed fold-storage planner. Protected17 and original streams are preserved.

New exact fifty-bit fold schedule uses7 carry wires versus8 in native tests,
at emitted componentCCX130 versus113;65536 common affine inputs per plan pass
value/phase/ancilla checks. Configured cap1233 now generates, but actualglobal
peak is1237 in square. Caps1232/1230 still fail. No generated count is a score.
All six terminal archives23/22/40/47/35/39 members verify locally.

Active: breakthrough-fold-square-20261020 supervisor2361166. Keep original
square chunk planning while borrowing source pivots to enforce the global
width. Native carryout extension and prior controls run before caps1234/1233;
baseline must remain exact13f6. Then inspect full ownership and actual replay
cost before any final source/census declaration. New submissions remain queued.
Run log: experiments/autorun-20261020-breakthrough/LOG.md.

'''
patch=[]
for name in['docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']:
    p=root/name;head=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode();first,rest=head.split('\n',1)
    assert prefix.split('\n')[0]not in head
    updated=first+'\n\n'+prefix+rest.lstrip('\n')
    patch.extend(difflib.unified_diff(head.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name))
    data=p.read_bytes();first,rest=data.split(b'\n',1);ending=b'\r\n'if first.endswith(b'\r')else b'\n'
    if rest.startswith(ending):rest=rest[len(ending):]
    p.write_bytes(first+b'\n'+ending+prefix.encode().replace(b'\n',ending)+rest)
(r/'checkpoint-carry-index.patch').write_text(''.join(patch),encoding='utf8',newline='\n')
with(r/'LOG.md').open('a',encoding='utf8')as f:f.write(f'\n- {stamp.isoformat()}: carry cycle checkpoint, six terminal archives locally verified. No new complete score or final gate/nonce. Fold-square2361166 active; existing user edits and accepted source preserved.\n')
print('Carry checkpoint and additive index patch saved.')
