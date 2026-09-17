# Usage and data compatibility

## Persistent state

The normal application starts with no DJs and default time bands. Add your own roster in the DJs tab. Removing a DJ deactivates it and retains its historical sets; re-adding the same exact name restores the active entry. Names are trimmed but personal aliases are not inferred.

Roster, bands, constraints, current lineup, locks and event fields are saved in SQLite. Changes are saved during relevant actions and on normal application exit. Forced termination may lose recent unsaved edits. Closing a demo discards all its data.

For a new event, update its name/date/times, attendance and time constraints, review locks, then regenerate. Old lineups remain visible until regeneration; validation detects changed time boundaries or attendance. Archive exactly once when final. Clearing history removes all archived sets and resets their influence on fairness; it does not erase the active roster.

Back up an old SQLite database before using `--database` to open it. Old real names and aliases remain private database content; they are not normalized against the previous association-specific name map. This is intentional.

## Language

The interface, application messages and exported worksheets use English. User-entered names, event titles and existing database values are preserved as entered. The legacy importer still recognizes the original French worksheet names below; these are file-format identifiers, not UI labels.

## Excel import

The **Import Excel** action supports the previous workbook format. It replaces imported roster, bands and history when present and uses the last event row as the current event. Existing lineup and locks are cleared. Check all imported fields before generating; import is intended for known legacy workbooks, not arbitrary spreadsheets.

| Worksheet | Expected columns |
| --- | --- |
| `DJs` | Name in column A, header in row 1 |
| `Valeurs horaires` | Start, end, numeric value |
| `Soirées` | ID, name, date, start, end; optional status in column I |
| `Planning` | Event ID in A, start in C, end in D, DJ in E, numeric value in G |
| `Disponibilités` | DJ names in A; event IDs across row 1; `oui`, `yes`, `1` or `true` for attendance |

Blank time limits must be entered manually after import. Formula cells are not evaluated. The formatted export is a human-readable schedule and **is not** the legacy import format.

## Screenshots

All committed screenshots are captured from the running QML UI using the bundled fictional scenario. To regenerate:

```bash
python scripts/capture_screenshots.py
```

This uses Qt's offscreen/software renderer and replaces the PNG files in `docs/images/`. It does not open personal databases.

## Desktop troubleshooting

A regular interactive launch requires a graphical session. On a minimal Linux installation, Qt may require system X11/Wayland and OpenGL libraries; use the missing library reported by Qt to identify the relevant distribution package. Do not set the offscreen backend for ordinary interactive use.

For headless verification, use `QT_QPA_PLATFORM=offscreen` and `QT_QUICK_BACKEND=software`; the tests configure these automatically. Native drag/drop behavior and file dialogs still deserve a manual check on each target desktop before a binary release.
