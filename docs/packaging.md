# Native release strategy

Publish source first. Keep native binaries separate from the source tree and defer automated binary releases until a target-OS smoke test has passed.

## Candidate build

```bash
python -m pip install ".[packaging]"
python scripts/build_app.py
```

The helper uses PyInstaller's default one-folder mode and collects packaged QML and demo resources. Build output goes into `dist/`; the build directory and generated spec are ignored. The helper is a starting point, not a claim of verified native distribution.

| Target | Build environment | Candidate artifact | Before release |
| --- | --- | --- | --- |
| Windows | Windows with supported Python | ZIP containing `DJPlanner.exe` and adjacent files | Test without Python installed; consider code signing |
| Linux | Linux with a compatible baseline distribution | Archive of the `DJPlanner` directory | Test system-library compatibility on target distributions |
| macOS | macOS, matching target architecture | `DJPlanner.app` | Test Apple Silicon/Intel as applicable; sign and notarize for broad distribution |

PyInstaller builds are specific to the operating system and interpreter used. It is not a cross-compiler. See [the official operating-mode documentation](https://pyinstaller.org/en/stable/operating-mode.html).

For the first release, install on a clean target machine, open all five screens, generate the demo, drag and lock slots, import/export a fictional workbook, archive, close and reopen the normal database. Include checksums and license notices with artifacts. Only then automate those native builds in a separate manually triggered workflow.

## Third-party licenses

The MIT license applies to DJ Planner's own code. It permits reuse and modification while requiring preservation of the copyright and permission notice; see the [MIT license text](https://opensource.org/license/mit).

Bundling dependencies does not relicense them as MIT. In particular, Qt for Python has its own licensing terms; consult the [official Qt for Python license documentation](https://doc.qt.io/qtforpython-6/licenses.html) and retain the relevant third-party notices. Review the licenses of the actual dependency versions included in every binary release. Keeping this source repository MIT does not itself settle the redistribution requirements for bundled Qt libraries.
