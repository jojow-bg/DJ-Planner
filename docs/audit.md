# Public-release audit

The source for this work was the latest available RC2.2 archive, including its visual and drag/drop fixes. The original archive was preserved separately and is not included in this repository or its Git history.

## Inventory and decisions

All 27 archived files were inspected. There were no bundled SQLite databases, virtual environments, Python caches, logs, exports, binaries or images. Earlier project versions existed as separate archives, not nested inside this one.

| Original files | Decision |
| --- | --- |
| `planner_core.py` | Retain solver and fairness weights; remove personal alias map; extend schedule validation and solver status handling |
| `bridge.py` | Retain orchestration and models; remove real roster; allow database injection; persist manual schedules; avoid restoring deleted default entries |
| `data_store.py` | Retain schema for used data; move default database outside source; omit creation of two unused event tables without dropping any existing tables |
| `excel_bridge.py` | Retain legacy compatibility; correct per-row duration; export user strings as literal cells |
| `main.py` | Replace with package entry point, `QApplication`, database selection and isolated demo mode |
| `build_app.py` | Move to `scripts/`; adapt to package resources and generic app identity |
| `requirements.txt` | Replace with `pyproject.toml`; separate runtime, development and packaging dependencies |
| `qml/Main.qml` | Keep dark palette/navigation; replace prerelease/internal branding |
| `qml/Planning.qml` | Keep layout and controls; remove redundant conditional |
| `qml/DJs.qml`, `qml/Bands.qml`, `qml/History.qml`, `qml/Stats.qml` | Retain existing screens |
| `qml/Theme.qml`, `qml/qmldir` | Retain singleton theme |
| `qml/components/Card.qml`, `DarkCheckBox.qml`, `DarkField.qml`, `DarkScrollBar.qml`, `PrimaryButton.qml` | Retain reusable dark controls |
| `qml/components/TimelineCard.qml` | Retain drag logic; prevent event stealing; reset position before model changes; expose a stable test identifier |
| `CORRECTIONS_QML_RC2_2.txt`, `CORRECTION_RC2_1.txt` | Do not carry version-specific working notes into the new repository |
| `README_QML_RC2.txt` | Replace with English README and focused usage/solver documentation |
| `VERIFICATION_QML_RC2.txt`, `VERIFICATION_RC2_1.txt`, `VERIFICATION_RC2_2.txt` | Replace static verification claims with executable tests and explicit validation status |

## Privacy

- Removed the hard-coded real roster and its personal nickname mapping.
- Removed association-specific organization and bundle identifiers.
- Removed the special-case import preference for a historical event ID.
- New examples and screenshots use only fictional stage names and events.
- No personal database, actual event workbook, local absolute source path, credential or private email is included in the release tree.
- Git ignores databases (including SQLite journal/WAL files), logs, spreadsheet exports, caches, build output, IDE settings and local environment files.
- Git history begins from a clean project shell. The original private source archive is not committed, so removing data in a later commit is not relied upon for privacy.

## Target structure

A single installable Python package is sufficient. QML and demo JSON are package resources. The solver remains independent of Qt, persistence remains SQLite, and the bridge orchestrates both. No service layer, server, plugin framework or wholesale solver rewrite was introduced.

## Defects corrected

1. Widget file dialogs now run under `QApplication`, not `QGuiApplication`.
2. Excel rows now use each set's actual duration, including the final remainder.
3. Current/manual lineup state is saved and restored alongside constraints and locks.
4. Empty rosters and deliberately empty band lists remain empty after restarting.
5. Validation catches stale boundaries, invalid indices and nonpositive durations in addition to roster/window violations.
6. Timeout without a solution is no longer labeled proven infeasibility.
7. Spreadsheet export treats text as text even when it starts with `=`.
8. Excel import clears stale lineup/locks and uses a generic last-event selection.
9. Timeline position is reset before the model can destroy/recreate the dragged delegate.

## Deliberately retained limitations

See the README and `solver.md`: one event at a time, conditional rounding, fixed fairness weights, synchronous solving, English-only UI, no archive deduplication, and limited legacy Excel import. These are documented rather than disguised as completed features.

## English presentation update

All application labels, status/error messages, solver diagnostics, comments and exported worksheet headers now use English. The five screenshots and usage instructions were refreshed. Existing French legacy workbook identifiers and user-entered data are preserved for compatibility. Scheduling rules and database keys are unchanged.
