from pathlib import Path
import hashlib,json,tarfile
R=Path(__file__).resolve().parent
sha=lambda data:hashlib.sha256(data).hexdigest()
archive=R/'evidence.tar.gz';assert sha(archive.read_bytes())=='814a8e74aa0c4990e29cddf120a6739c117c45df773544bc6f83d5594ac58b87'
with tarfile.open(archive)as t:
 manifest=json.load(t.extractfile('MANIFEST.json'))
 names=['mr-mask-all70.json','BASE-BINDING.json','global.json','RUN-RECEIPT.json','BEFORE-PINS.json','AFTER-PINS.json','tool/src/mask_program_trace.rs']
 data={name:t.extractfile(name).read()for name in names}
 for name,raw in data.items():assert sha(raw)==manifest[name],name
metadata=json.loads(data['mr-mask-all70.json']);binding=json.loads(data['BASE-BINDING.json']);report=json.loads(data['global.json'])
assert metadata['original_stream_sha256']=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
assert metadata['source_commit']=='4b2ec52fc55da796aa8f5ef851290297e8706424'
assert report['source_stream_sha256']==binding['stream_sha256']=='06cdc5de3dadbe23a2ff306466ec2ef27514bed53be1145ec83bdf490cb99a7a'
assert json.loads(data['BEFORE-PINS.json'])==json.loads(data['AFTER-PINS.json'])
assert report['old_mask_transfer_used']is False
sidecar={'status':'REQUIRED_FRESH_ALL70_SOURCE_BINDING_CLARIFICATION_NO_RUNTIME_AUTHORITY',
 'program_path':'mr-mask-all70.bin','program_sha256':'1e3092db38ecfca8a6583829852ad7302ba13c38629474c6ea808c5637677c60',
 'raw_export_manifest_path':'mr-mask-all70.json','raw_export_manifest_sha256':sha(data['mr-mask-all70.json']),
 'evaluated_source_stream_sha256':binding['stream_sha256'],
 'preserved_original_archive_sha256':sha(archive.read_bytes()),
 'invalid_legacy_exporter_fields':{'original_stream_sha256':metadata['original_stream_sha256'],'source_commit':metadata['source_commit']},
 'cause':'The unchanged generic exporter hardcodes these two labels at mask_program_trace.rs line33. They do not identify the stream loaded by this fresh query. No graph, kernel, program bytes or proof result changed for this clarification.',
 'authoritative_fresh_binding':{'BASE-BINDING.json':sha(data['BASE-BINDING.json']),'global.json':sha(data['global.json']),'RUN-RECEIPT.json':sha(data['RUN-RECEIPT.json']),'BEFORE-PINS.json':sha(data['BEFORE-PINS.json']),'AFTER-PINS.json':sha(data['AFTER-PINS.json'])},
 'exporter_source_sha256':sha(data['tool/src/mask_program_trace.rs']),
 'consumer_requirement':'Before any downstream runtime or transfer, validate this sidecar program hash AND raw manifest hash AND evaluated source06 hash against the fresh proof/source receipts. Reject a binding based only on the legacy2a labels. The original2a mask and its runtime remain separate and unchanged.',
 'authority':False,'program_or_proof_rerun':False}
(R/'EXPORT-METADATA-CLARIFICATION.json').write_bytes((json.dumps(sidecar,indent=2)+'\n').encode())
files={name:raw for name,raw in data.items()};files['EXPORT-METADATA-CLARIFICATION.json']=(R/'EXPORT-METADATA-CLARIFICATION.json').read_bytes();files['clarify-metadata.py']=Path(__file__).read_bytes()
manifest2={name:sha(raw)for name,raw in files.items()}
(R/'METADATA-SUPPLEMENT-MANIFEST.json').write_bytes((json.dumps(manifest2,indent=2)+'\n').encode())
import io
with tarfile.open(R/'metadata-supplement.tar.gz','w:gz')as t:
 for name,raw in files.items():
  info=tarfile.TarInfo(name);info.size=len(raw);t.addfile(info,io.BytesIO(raw))
 t.add(R/'METADATA-SUPPLEMENT-MANIFEST.json',arcname='METADATA-SUPPLEMENT-MANIFEST.json')
with tarfile.open(R/'metadata-supplement.tar.gz')as t:
 for name,h in manifest2.items():assert sha(t.extractfile(name).read())==h
receipt={'status':'VERIFIED','archive_sha256':sha((R/'metadata-supplement.tar.gz').read_bytes()),'verified_members':len(manifest2),'required_sidecar_sha256':sha((R/'EXPORT-METADATA-CLARIFICATION.json').read_bytes()),'original_archive_unchanged_sha256':sha(archive.read_bytes())}
(R/'METADATA-SUPPLEMENT-RECEIPT.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
