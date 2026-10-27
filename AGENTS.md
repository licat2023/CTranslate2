# Fork build guidelines

- Preserve upstream GPU targets when changing `PYTORCH_ROCM_ARCH` in `python/tools/prepare_build_environment_windows_rocm.sh`.
- The custom package version is defined in `python/ctranslate2/version.py`; increment its local build suffix when changing released content.
- `.github/workflows/rocm-wheels.yml` builds regular CPython 3.12, 3.13 and 3.14 Windows x64 wheels. Inherited upstream CI jobs are restricted to the upstream repository.
- `.github/scripts/validate_rocm_wheels.py` checks wheel identity, Python ABI, bundled runtimes and embedded GPU target coverage. Its report records asset hashes.
- GitHub runners do not validate Radeon 780M inference. Before release, test imports and clean exits on each Python ABI, then actual float16 and int8_float16 transcription on the 780M with recorded runtime DLL paths.
- Upload verified `.whl` assets and their manifest to an immutable GitHub Release. Keep build outputs and downloaded runtimes out of Git.
