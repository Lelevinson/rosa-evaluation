"""Read-only integrity checks; write only a new dated preparation checkpoint."""
import hashlib
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
EVAL = STAGE.parents[3]
WORKSPACE = EVAL.parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    guide = STAGE / 'resolution-guide-20261117'
    packet = guide / 'reviewer-packet'
    archive = guide / 'G1_FOUR_CASE_HUMAN_REVIEW_2026-11-17.zip'
    expected = (guide / (archive.name + '.sha256')).read_text().split()[0]
    assert sha(archive.read_bytes()) == expected
    files = json.loads((packet / 'PACKET_MANIFEST.json').read_text())['files']
    for name, digest in files.items():
        assert sha((packet / name).read_bytes()) == digest, name
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name in z.namelist():
            assert z.read(name) == (packet / name).read_bytes(), name
        assert not any('private' in name.lower() for name in z.namelist())
        archive_files = len(z.namelist())
    seal_folder = STAGE / 'scorer-review/astra-review-20261115'
    seal = json.loads((seal_folder / 'seal-manifest.json').read_text())
    for name, digest in seal['artifacts_sha256'].items():
        path = WORKSPACE / name
        if not path.exists():
            path = seal_folder / name
        assert sha(path.read_bytes()) == digest, name
    result = {'date': '2026-11-19', 'kind': 'READ_ONLY_G1_STAGE3_RESUMPTION_CHECK',
        'packet_crc_and_hashes_pass': True, 'packet_files': archive_files,
        'packet_transcripts': 4, 'packet_sha256': expected,
        'sealed_astra_review_files_pass': len(seal['artifacts_sha256']),
        'experimental_inference_requests': 0, 'human_ratings_received': False,
        'methodological_amendments_awaiting_confirmation': True,
        'held_out_launch_authorized': False,
        'checker_correction': "First helper attempt used nonexistent seal key files; corrected to artifacts_sha256. No historical manifest or evidence was edited.",
        'note': 'Legacy checksum-guard result is recorded separately; it is not relabeled PASS.'}
    (HERE / 'READINESS_VERIFICATION.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
