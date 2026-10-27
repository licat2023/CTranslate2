"""Check release wheel metadata and embedded HIP architecture coverage."""
import argparse
from email.parser import BytesParser
import hashlib
import json
from pathlib import Path
import re
import zipfile

TARGETS = {'gfx1030', 'gfx1100', 'gfx1101', 'gfx1102', 'gfx1103',
           'gfx1150', 'gfx1151', 'gfx1200', 'gfx1201'}
ABIS = {'cp312', 'cp313', 'cp314'}


def inspect(path, version):
    with zipfile.ZipFile(path) as wheel:
        metadata_path = next(name for name in wheel.namelist() if name.endswith('.dist-info/METADATA'))
        metadata = BytesParser().parsebytes(wheel.read(metadata_path))
        if metadata['Name'] != 'ctranslate2' or metadata['Version'] != version:
            raise ValueError(f'{path.name}: unexpected package identity')
        library = wheel.read('ctranslate2/ctranslate2.dll')
        targets = {target.decode() for target in re.findall(
            rb'hipv4-amdgcn-amd-amdhsa--(gfx[0-9a-z]+)', library)}
        if not TARGETS <= targets:
            raise ValueError(f'{path.name}: missing targets {sorted(TARGETS - targets)}')
        abi = path.name.rsplit('-', 3)[1]
        if abi not in ABIS or not path.name.endswith(f'-{abi}-{abi}-win_amd64.whl'):
            raise ValueError(f'{path.name}: unexpected Python ABI or platform')
        if f'ctranslate2/_ext.{abi}-win_amd64.pyd' not in wheel.namelist():
            raise ValueError(f'{path.name}: missing matching Python extension')
        if 'ctranslate2/libiomp5md.dll' not in wheel.namelist():
            raise ValueError(f'{path.name}: missing OpenMP runtime')
    return {'filename': path.name, 'version': version, 'abi': abi,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'bytes': path.stat().st_size, 'gpu_targets': sorted(targets)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    parser.add_argument('--version', required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    records = [inspect(path, args.version) for path in sorted(args.directory.glob('*.whl'))]
    if {record['abi'] for record in records} != ABIS or len(records) != len(ABIS):
        raise ValueError('Expected exactly one Windows wheel for each of cp312, cp313 and cp314')
    args.report.write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(records, indent=2))


if __name__ == '__main__':
    main()
