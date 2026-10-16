"""Root archive/source reviews and a complete recount of the fixed seed cohort."""
from pathlib import Path, PurePosixPath
import hashlib, json, tarfile

ROOT = Path(__file__).resolve().parents[2] / 'experiments'
sha = lambda b: hashlib.sha256(b).hexdigest()
cases = [
    ('all70-zero-mr-20261016', 'evidence.tar.gz', 'b9fdff4b3f08f2fd380f69938fdfddfed09a65ca076c7991b160ba12e0a6cc7d'),
    ('seed-restore-20261016', 'terminal-v1.tar.gz', '10b984fdd3fd878b75882b5cbb7c7eec8d3684f61d6b7388e751b796d81cef7f'),
    ('census-all74-fixed67-20261016', 'native-base-evidence-v1.tar.gz', '0489ce22aab173c06878fa409d2c4bc4cee84f820aea679e41669a2c5a4997c8'),
]
for folder, name, expected in cases:
    path = ROOT / folder / name
    assert sha(path.read_bytes()) == expected
    with tarfile.open(path) as archive:
        members = archive.getmembers()
        names = [m.name for m in members]
        assert len(names) == len(set(names))
        assert all((m.isfile() or m.isdir()) and not PurePosixPath(m.name).is_absolute()
                   and '..' not in PurePosixPath(m.name).parts for m in members)
        read = lambda n: archive.extractfile(n).read()
        def find(name):
            found = [n for n in names if n == name or n.endswith('/' + name)]
            assert len(found) == 1, (name, found)
            return found[0]
        load = lambda name: json.loads(read(find(name)))
        manifest_name = find('MANIFEST.json')
        manifest = json.loads(read(manifest_name))
        prefix = manifest_name[:-len('MANIFEST.json')]
        files = manifest.get('files', manifest)
        for filename, detail in files.items():
            raw = read(prefix + filename)
            if isinstance(detail, str):
                assert sha(raw) == detail, filename
            else:
                assert len(raw) == detail['bytes'] and sha(raw) == detail['sha256'], filename
        if folder == 'all70-zero-mr-20261016':
            binding = load('IR-BINDING.json')
            assert binding['source_stream_sha256'] == '06cdc5de3dadbe23a2ff306466ec2ef27514bed53be1145ec83bdf490cb99a7a'
            assert binding['program_sha256'] == 'a805af2e120bc191062d6901cbcd4d4a390abba814f3a2fd5007d4b0b46c3859'
            assert binding['required_mask_source_sidecar_sha256'] == 'bfd68eae7215bfadaa0222b62203ec5cf6dc12c987af30ba6084c4282b07d485'
            assert not binding['runtime_or_search_authority'] and not binding['phase_or_pass_authority']
            assert load('SOURCE-PINS-BEFORE.json') == load('SOURCE-PINS-AFTER.json')
            assert read('run-v2.exit').strip() == b'0' and read('failed-v1/run.exit').strip() == b'1'
            assert sha(read('tool/src/main.rs')) == binding['compiler_source_sha256'] == '6544214601c6fcfce8a3ea4f97838abce31ed002548b2b200cc24cd96d313e67'
            assert sha(read('tool/zero8.c')) == binding['C_kernel_source_sha256'] == '198490b80d502dd6a53c0de33e733a43a5e9a26b7e6829b9c00ef5c119742128'
            log = read('validation.log').decode()
            assert all(v in log for v in ['SLICE_FIXTURES assignments=512', 'ZERO_VALUE_VERIFIED shots=512', 'SLICE_VERIFIED shots=512'])
            extra = read('extra-validation.log').decode()
            assert 'FRESH_ALL70_ZERO_IR_ALL_CONTROLS_PASS' in extra and extra.count('FRESH_ALL70_ZERO_IR_CONTROL_PASS') == 16
            metadata = read('all70.compact16.bin.tsv').decode().splitlines()
            assert sum(line.startswith('output\t') for line in metadata) == 512
            detail = dict(fresh06_binding=True, protected_generic_compiler_and_C_kernel_unchanged=True,
                          all512_outputs_and_recorded_controls_checked=True, phase_or_runtime_authority=False)
            output = 'ROOT_ZERO_IR_REVIEW.json'
        elif folder == 'seed-restore-20261016':
            data = []
            for role in ['parent', 'candidate']:
                rows = {}
                for raw in read(prefix + 'seed-fresh/' + role + '.jsonl').splitlines():
                    row = json.loads(raw)
                    assert row['batch'] not in rows and 0 <= row['batch'] < 32768 and row['shots'] == 64
                    assert len({f['lane'] for f in row['failures']}) == len(row['failures'])
                    for kind in ['value', 'phase', 'dirty']:
                        assert row[kind + '_shots'] == sum(bool(f.get(kind, False)) for f in row['failures'])
                    rows[row['batch']] = row
                assert len(rows) == 32768
                data.append(rows)
            a, b = data
            for i in range(32768):
                assert b[i]['toffoli'] - a[i]['toffoli'] == 64
                assert {k: v for k, v in a[i].items() if k != 'toffoli'} == {k: v for k, v in b[i].items() if k != 'toffoli'}
            counts = dict(failed_batches=sum(bool(r['failures']) for r in a.values()),
                          **{k + '_shots': sum(r[k + '_shots'] for r in a.values()) for k in ['value', 'phase', 'dirty']})
            assert counts == dict(failed_batches=4214, value_shots=3622, phase_shots=2723, dirty_shots=0)
            detail = dict(all65536_raw_rows_recounted=True, counts_each=counts, exact_one_T_per_shot=True,
                          all_failure_records_equal=True, lambda_each=4214 * 141 / 32768,
                          strict_failure_gate_pass=False, no_new_census_or_resampling=True)
            output = 'ROOT_TERMINAL_RECOUNT.json'
        else:
            receipt = load('BASE_NATIVE_RECEIPT.json')
            assert receipt['status'] == 'FULL_NATIVE_ONLY_ALL74_ORIGINAL_DELETED_CCX_RESTORED_PASS'
            assert receipt['source_sha256'] == 'd6e7091b3952519e383eb7e0093c802035de26a5c3b65ea23e8e54b0169ab91a'
            assert receipt['restored'] == 74 and receipt['all70_reductions_retained']
            assert receipt['every_other_original_Op_identical'] and receipt['old_MR_draw_ordinals_unchanged']
            assert (receipt['Q'], receipt['B'], receipt['MR']) == (1234, 45701, 906156)
            assert receipt['diff_paths'] == ['src/point_add/census_cut.rs']
            assert len(receipt['protected_files_sha256']) == 17
            source = receipt['source_files_sha256']
            for rel, digest in source.items():
                matches = [n for n in names if n.endswith('/src/point_add/' + rel) or n == 'src/point_add/' + rel]
                assert len(matches) == 1 and sha(read(matches[0])) == digest, rel
            detail = dict(full_source_files=len(source), protected_manifest_files=17, original74_restored=True,
                          remaining70_reductions_retained=True, native_receipt_scope_reviewed=True,
                          no_new_fullstream_semantic_execution=True)
            output = 'ROOT_BASE_ARCHIVE_REVIEW.json'
        result = dict(status='ROOT_ARCHIVE_AND_RECORDED_EVIDENCE_REVIEW_PASS', archive_sha256=expected,
                      verified_members=len(files), **detail)
        (ROOT / folder / output).write_text(json.dumps(result, indent=2) + '\n')
        print(folder, json.dumps(result))
