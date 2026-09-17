# Validation status

Validation performed on 2026-09-16 against the prepared public-release source.

The English presentation update was checked with the same regression suite, including legacy French workbook import and English worksheet/header export. All five UI screenshots were regenerated in English. User-entered data is not translated.

| Check | Result |
| --- | --- |
| pytest | 35 tests passed locally |
| Installed-wheel tests from outside the source directory | 35 tests passed |
| Ruff static checks and formatting | Passed |
| Python source distribution and wheel build | Passed |
| Fresh virtual environment installation from the wheel | Passed |
| CLI help | Passed |
| Full demo startup and normal shutdown from the installed wheel | Passed with offscreen Qt |
| All five QML screens | Loaded without QML warnings |
| Timeline mouse drag and double-click locking | Passed with QtTest mouse events |
| Screenshot capture and visual review | Five real UI screenshots using fictional data |
| Release-tree privacy scan | No matches for the original private roster, association identifiers, local user paths or searched credential patterns |
| GitHub Actions | Configured; not run remotely yet |
| Windows/macOS desktop behavior | Not locally tested |
| Native PyInstaller binaries | Strategy/helper prepared; no binary build claimed |

Local runtime: Linux x86_64, Python 3.12.14, PySide6 6.11.2, OR-Tools 9.15.6755, openpyxl 3.1.5 and platformdirs 4.11.8. Tests use pytest 9.1.1. Versions above describe the verified environment, not a promise of testing every allowed version.

The mouse tests exercise the real QML controls, but an offscreen test is not a substitute for manually checking native dialogs, window-manager behavior and packaging on each OS. The CI matrix is intended to provide additional installation and regression evidence once the repository exists.

The privacy audit covers the retrieved source archive and the prepared release tree. It cannot certify unrelated local files or later user imports. The original private archive is not part of the Git history.
