"""Write the dated coordinator checkpoint; diagnostic experiments stay out of plots."""
from pathlib import Path
import hashlib,json
base=Path(__file__).resolve().parents[2]
for rel in ['README.md','docs/AGENT_HANDOFF.md','docs/research-plan.md','docs/results-status.md']:
    p=base/rel
    text=p.read_text(encoding='utf-8').replace('05:15','05:09')
    p.write_text(text,encoding='utf-8')
log=base/'experiments/autorun-20261015-2239/LOG.md'
with log.open('a',encoding='utf-8') as out:
    out.write('\n- 05:09 Positive repaired53 qualification: native18tests/stream13d1f734 PASS; independently rehashed170completepointaddfiles includingtables, protectedharnessunchanged. Solefixed32768census4185parent/4141candidate failedbatches, lambda18.007965/17.818634, zero dirty, net39.349014+/-.509027T/Q1234. Value3553→3539shots,12parent-only/0candidate-only batches; not a demonstrated1.1floorcure. A29-relative53universalaudit andfreshA29maskactive; original4bmask/IRinvalid. RootfreshA29zeroMRa408f996 passes512protectedallq/b+512scopefixtures;24artifactarchiveverified, no phase/MRindependenceclaim.\n')
    out.write('- 05:09 Searchsnapshot05:06:01:12410880completed distinct/lowerprefix12345344,no pass,65filearchiveb5e0c504... independentlyverified; activeproductionunchanged. Public05:06refresh1572/1231/51: newQ677/T950615823/source d9d5e991.../submission18912d63, T753771/product939347948 unchanged. BestcompletequeuedT753721/Q1468; noexternal submission.\n')
    out.write('- 05:09 Independentlyverified3390productartifactbaseaa137f82... andall3444targets from compact supplementa8fedefb...; full native repaired-source170files separatelyverified. Cap2048 actualQ1560 adds1anchoredT; cap4096resourcefailure24GiB preserved; wide151neverlaunched. Backseam521artifactsverified: fixed4096same531fails/558shots asparent, lambda18.27905>18, noresample/search/composite. Freeborrow208artifactsverified; allsource-negative. Flag12universal24componentcontracts/12wrongcleanupnegativesPASS,native/freshpending; cachedcompositionmustadmitnewlowerreadsanddonorleases.\n')
    out.write('- 05:09 Rootstrictcommon-control/fanoutqueries bothnegativeon4frozenstreams,20artifactarchiveverified; nocandidate. NUMA43artifactarchiveverified: medians17.630565unbound/18.275030bound,3.66%slower; noactiveaffinitychange. Correctedlazyintegrationreview10artifactsverified, priorReady-onlyreviewmisspreserved. Sourcecollectorhasmanifest.json ratherthanreceipt.json; initialcopyrequestmissingreceiptfailedafterarchivescopied, embeddedhashesallverified.\n')
result=[]
for rel in ['repair-zero-mr-20261016','dirty-fanout-20261016','back-seam-repair-20261016','free-borrow-family-20261016']:
    p=base/'experiments'/rel
    manifest=json.loads((p/'verified-manifest.json').read_text())
    result.append({'experiment':rel,'archive_sha256':hashlib.sha256((p/'evidence.tar.gz').read_bytes()).hexdigest(),'verified_files':len(manifest.get('files',manifest))})
(base/'experiments/autorun-20261015-2239/CHECKPOINT-0509-ARCHIVES.json').write_text(json.dumps(result,indent=2)+'\n')
print('Dated checkpoint and archive hashes saved')
