from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date
from typing import List

from PySide6.QtCore import QObject, Property, Signal, Slot, QAbstractListModel, QModelIndex, Qt
from PySide6.QtWidgets import QFileDialog

from .planner_core import (
    DJConstraint,
    HistorySet,
    ScheduleRow,
    solve_schedule,
    validate_schedule,
    history_stats,
)
from .data_store import DataStore
from .excel_bridge import import_v2, export_schedule


DEFAULT_BANDS = [
    ("20:00", "21:00", 1),
    ("21:00", "22:00", 2),
    ("22:00", "23:00", 4),
    ("23:00", "00:00", 5),
    ("00:00", "01:00", 5),
    ("01:00", "02:00", 3),
]


class DictListModel(QAbstractListModel):
    def __init__(self, rows=None, roles=None):
        super().__init__()
        self._rows = rows or []
        self._roles = roles or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._rows)

    def roleNames(self):
        return {Qt.UserRole + 1 + i: name.encode() for i, name in enumerate(self._roles)}

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        role_index = role - Qt.UserRole - 1
        if 0 <= role_index < len(self._roles):
            return self._rows[index.row()].get(self._roles[role_index])
        return None

    def reset_rows(self, rows):
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def rows(self):
        return self._rows


class DJPlannerBridge(QObject):
    statusChanged = Signal()
    partyChanged = Signal()
    errorRaised = Signal(str)
    infoRaised = Signal(str)
    selectedTabChanged = Signal()

    def __init__(self, db_path=None):
        super().__init__()
        self.store = DataStore(db_path)

        self._status = "Ready"
        self._party_name = self.store.get_setting("party_name", "New event")
        self._party_date = self.store.get_setting("party_date", str(date.today()))
        self._party_start = self.store.get_setting("party_start", "20:00")
        self._party_end = self.store.get_setting("party_end", "02:00")
        self._selected_tab = 0

        self.roster = self.store.get_djs()
        if self.store.get_setting("initialized") != "1":
            self.store.replace_bands(DEFAULT_BANDS)
            self.store.set_setting("initialized", "1")
        self.bands = self.store.get_bands()
        self.history = self.store.get_history(HistorySet)
        self.schedule: List[ScheduleRow] = []
        self.locks = {}

        raw_constraints = self.store.get_setting("constraints_json", "{}")
        try:
            self.constraints_state = json.loads(raw_constraints or "{}")
        except Exception:
            self.constraints_state = {}

        raw_locks = self.store.get_setting("locks_json", "{}")
        try:
            self.locks = {int(k): v for k, v in json.loads(raw_locks or "{}").items()}
        except Exception:
            self.locks = {}

        self.dj_model = DictListModel([], ["name", "present", "minTime", "maxTime"])
        self.schedule_model = DictListModel(
            [], ["slotIndex", "dj", "start", "end", "duration", "value", "locked"]
        )
        self.band_model = DictListModel([], ["start", "end", "value"])
        self.history_model = DictListModel(
            [], ["party", "date", "dj", "start", "end", "value", "position"]
        )
        self.stats_model = DictListModel(
            [], ["dj", "sets", "minutes", "avgValue", "avgPosition", "latest"]
        )

        try:
            self.schedule = [
                ScheduleRow(**row)
                for row in json.loads(self.store.get_setting("schedule_json", "[]"))
            ]
        except (ValueError, TypeError):
            self.schedule = []
        self.refresh_all_models()

    # ---------- Properties ----------
    @Property(str, notify=statusChanged)
    def status(self):
        return self._status

    def _set_status(self, value):
        self._status = value
        self.statusChanged.emit()

    @Property(str, notify=partyChanged)
    def partyName(self):
        return self._party_name

    @partyName.setter
    def partyName(self, value):
        self._party_name = value
        self.partyChanged.emit()

    @Property(str, notify=partyChanged)
    def partyDate(self):
        return self._party_date

    @partyDate.setter
    def partyDate(self, value):
        self._party_date = value
        self.partyChanged.emit()

    @Property(str, notify=partyChanged)
    def partyStart(self):
        return self._party_start

    @partyStart.setter
    def partyStart(self, value):
        self._party_start = value
        self.partyChanged.emit()

    @Property(str, notify=partyChanged)
    def partyEnd(self):
        return self._party_end

    @partyEnd.setter
    def partyEnd(self, value):
        self._party_end = value
        self.partyChanged.emit()

    @Property(int, notify=selectedTabChanged)
    def selectedTab(self):
        return self._selected_tab

    @selectedTab.setter
    def selectedTab(self, value):
        self._selected_tab = int(value)
        self.selectedTabChanged.emit()

    @Property(QObject, constant=True)
    def djModel(self):
        return self.dj_model

    @Property(QObject, constant=True)
    def scheduleModel(self):
        return self.schedule_model

    @Property(QObject, constant=True)
    def bandModel(self):
        return self.band_model

    @Property(QObject, constant=True)
    def historyModel(self):
        return self.history_model

    @Property(QObject, constant=True)
    def statsModel(self):
        return self.stats_model

    # ---------- Model refresh ----------
    def refresh_all_models(self):
        self._refresh_djs()
        self._refresh_schedule()
        self._refresh_bands()
        self._refresh_history()
        self._refresh_stats()

    def _refresh_djs(self):
        rows = []
        for name in self.roster:
            state = self.constraints_state.get(name, {})
            rows.append(
                {
                    "name": name,
                    "present": bool(state.get("present", False)),
                    "minTime": state.get("min", ""),
                    "maxTime": state.get("max", ""),
                }
            )
        self.dj_model.reset_rows(rows)

    def _refresh_schedule(self):
        rows = []
        for r in self.schedule:
            rows.append(
                {
                    "slotIndex": r.slot_index,
                    "dj": r.dj,
                    "start": r.start,
                    "end": r.end,
                    "duration": int(round(r.end_abs - r.start_abs)),
                    "value": round(r.slot_value, 2),
                    "locked": bool(r.locked),
                }
            )
        self.schedule_model.reset_rows(rows)

    def _refresh_bands(self):
        self.band_model.reset_rows(
            [{"start": s, "end": e, "value": float(v)} for s, e, v in self.bands]
        )

    def _refresh_history(self):
        self.history_model.reset_rows(
            [
                {
                    "party": h.party_name,
                    "date": h.date,
                    "dj": h.dj,
                    "start": h.start,
                    "end": h.end,
                    "value": round(float(h.value or 0), 2),
                    "position": "" if h.position is None else round(float(h.position), 2),
                }
                for h in self.history
            ]
        )

    def _refresh_stats(self):
        stats = history_stats(self.history)
        rows = []
        for dj in self.roster:
            s = stats.get(
                dj,
                {"sets": 0, "minutes_sum": 0, "avg_value": 0, "avg_position": None, "latest": ""},
            )
            total = int(round(s.get("minutes_sum", 0)))
            h, m = divmod(total, 60)
            rows.append(
                {
                    "dj": dj,
                    "sets": s["sets"],
                    "minutes": f"{h}h {m:02d}m",
                    "avgValue": round(s["avg_value"], 2),
                    "avgPosition": "" if s["avg_position"] is None else round(s["avg_position"], 2),
                    "latest": s["latest"],
                }
            )
        self.stats_model.reset_rows(rows)

    # ---------- DJs ----------
    @Slot(int, bool, str, str)
    def updateDJ(self, index, present, min_time, max_time):
        if not (0 <= index < len(self.roster)):
            return
        name = self.roster[index]
        self.constraints_state[name] = {
            "present": bool(present),
            "min": min_time.strip(),
            "max": max_time.strip(),
        }
        self._refresh_djs()
        self.saveState()

    @Slot(str)
    def addDJ(self, name):
        name = name.strip()
        if not name:
            self.errorRaised.emit("DJ name cannot be empty.")
            return
        if name in self.roster:
            self.errorRaised.emit("This DJ already exists.")
            return
        self.roster.append(name)
        self.constraints_state[name] = {"present": False, "min": "", "max": ""}
        self.store.add_dj(name)
        self._refresh_djs()
        self._refresh_stats()
        self.saveState()
        self.infoRaised.emit(f"{name} has been added.")

    @Slot(int)
    def removeDJ(self, index):
        if not (0 <= index < len(self.roster)):
            return
        name = self.roster.pop(index)
        self.constraints_state.pop(name, None)
        self.store.remove_dj(name)
        self.schedule = []
        self.locks = {}
        self._refresh_djs()
        self._refresh_schedule()
        self._refresh_stats()
        self.saveState()
        self.infoRaised.emit(f"{name} has been removed from the active roster.")

    # ---------- Bands ----------
    @Slot(int, str, str, float)
    def updateBand(self, index, start, end, value):
        if not (0 <= index < len(self.bands)):
            return
        self.bands[index] = (start.strip(), end.strip(), float(value))
        self.store.replace_bands(self.bands)
        self._refresh_bands()

    @Slot()
    def addBand(self):
        self.bands.append(("20:00", "21:00", 1.0))
        self.store.replace_bands(self.bands)
        self._refresh_bands()

    @Slot(int)
    def removeBand(self, index):
        if 0 <= index < len(self.bands):
            self.bands.pop(index)
            self.store.replace_bands(self.bands)
            self._refresh_bands()

    # ---------- Planning ----------
    def _constraints(self):
        result = []
        for name in self.roster:
            s = self.constraints_state.get(name, {})
            result.append(
                DJConstraint(
                    name=name,
                    present=bool(s.get("present", False)),
                    min_time=s.get("min") or None,
                    max_time=s.get("max") or None,
                )
            )
        return result

    @Slot()
    def generate(self):
        try:
            self.schedule = solve_schedule(
                self._party_start,
                self._party_end,
                self._constraints(),
                self.bands,
                self.history,
                self.locks,
            )
            self._refresh_schedule()
            self._set_status(f"Schedule generated • {len(self.schedule)} DJs")
            self.saveState()
        except Exception as exc:
            self._set_status("Could not generate schedule")
            self.errorRaised.emit(str(exc))

    @Slot(int, int)
    def swapSlots(self, a, b):
        if a == b:
            return
        if not (0 <= a < len(self.schedule) and 0 <= b < len(self.schedule)):
            return
        if a in self.locks or b in self.locks:
            self.errorRaised.emit("Unlock both slots before swapping them.")
            return

        self.schedule[a].dj, self.schedule[b].dj = self.schedule[b].dj, self.schedule[a].dj
        self._refresh_schedule()

        errors = validate_schedule(
            self._party_start, self._party_end, self._constraints(), self.schedule
        )
        self.saveState()
        if errors:
            self._set_status("Schedule edited — constraints violated")
            self.errorRaised.emit("\n".join(errors))
        else:
            self._set_status("Valid swap")

    @Slot(int)
    def toggleLock(self, index):
        if not (0 <= index < len(self.schedule)):
            return
        if index in self.locks:
            self.locks.pop(index, None)
            self.schedule[index].locked = False
        else:
            self.locks[index] = self.schedule[index].dj
            self.schedule[index].locked = True
        self._refresh_schedule()
        self.saveState()

    @Slot(result=bool)
    def validateCurrent(self):
        if not self.schedule:
            self.errorRaised.emit("No schedule to validate.")
            return False
        errors = validate_schedule(
            self._party_start, self._party_end, self._constraints(), self.schedule
        )
        if errors:
            self.errorRaised.emit("\n".join(errors))
            return False
        self.infoRaised.emit("All hard constraints are satisfied.")
        return True

    @Slot()
    def archiveCurrent(self):
        if not self.validateCurrent():
            return
        pid = f"EVENT-{self._party_date}-{len(self.history) + 1}"
        n = len(self.schedule)
        new_rows = []
        for i, r in enumerate(self.schedule):
            new_rows.append(
                HistorySet(
                    party_id=pid,
                    party_name=self._party_name or pid,
                    date=self._party_date,
                    dj=r.dj,
                    start=r.start,
                    end=r.end,
                    value=r.slot_value,
                    position=0.5 if n <= 1 else i / (n - 1),
                )
            )
        self.history.extend(new_rows)
        self.store.replace_history(self.history)
        self._refresh_history()
        self._refresh_stats()
        self.infoRaised.emit("The event has been added to the history.")

    # ---------- Files ----------
    @Slot()
    def importExcel(self):
        path, _ = QFileDialog.getOpenFileName(
            None,
            "Import legacy Excel workbook",
            "",
            "Excel (*.xlsx)",
            options=QFileDialog.Option.DontUseNativeDialog,
        )
        if not path:
            return
        try:
            data = import_v2(path)
            if data["roster"]:
                self.roster = data["roster"]
            if data["bands"]:
                self.bands = data["bands"]
            self.history = data["history"]

            target = next(reversed(data["parties"].values()), None)
            self.schedule = []
            self.locks = {}
            self.constraints_state = {}

            if target:
                self._party_name = str(target.get("name") or "Event")
                self._party_date = str(target.get("date") or self._party_date)
                self._party_start = target.get("start") or self._party_start
                self._party_end = target.get("end") or self._party_end
                self.partyChanged.emit()

                availability = data["availability"].get(str(target.get("id", "")), {})
                self.constraints_state = {}
                for name in self.roster:
                    self.constraints_state[name] = {
                        "present": bool(availability.get(name, False)),
                        "min": "",
                        "max": "",
                    }

            self.store.replace_djs(self.roster)
            self.store.replace_bands(self.bands)
            self.store.replace_history(self.history)
            self.refresh_all_models()
            self.saveState()
            self.infoRaised.emit(
                f"Import complete: {len(self.roster)} DJs, {len(self.history)} historical sets."
            )
        except Exception as exc:
            self.errorRaised.emit(str(exc))

    @Slot()
    def exportExcel(self):
        if not self.validateCurrent():
            return
        path, _ = QFileDialog.getSaveFileName(
            None,
            "Export schedule",
            "DJ_Planner.xlsx",
            "Excel (*.xlsx)",
            options=QFileDialog.Option.DontUseNativeDialog,
        )
        if not path:
            return
        if not path.lower().endswith(".xlsx"):
            path += ".xlsx"
        try:
            export_schedule(
                path,
                {"name": self._party_name, "date": self._party_date},
                self.schedule,
                history_stats(self.history),
            )
            self.infoRaised.emit(f"Schedule exported to:\n{path}")
        except Exception as exc:
            self.errorRaised.emit(str(exc))

    @Slot()
    def clearHistory(self):
        self.history = []
        self.store.clear_history()
        self._refresh_history()
        self._refresh_stats()

    # ---------- Persistence ----------
    @Slot()
    def saveState(self):
        self.store.replace_djs(self.roster)
        self.store.replace_bands(self.bands)
        self.store.replace_history(self.history)
        self.store.set_setting("party_name", self._party_name)
        self.store.set_setting("party_date", self._party_date)
        self.store.set_setting("party_start", self._party_start)
        self.store.set_setting("party_end", self._party_end)
        self.store.set_setting(
            "constraints_json", json.dumps(self.constraints_state, ensure_ascii=False)
        )
        self.store.set_setting(
            "locks_json", json.dumps({str(k): v for k, v in self.locks.items()}, ensure_ascii=False)
        )
        self.store.set_setting("schedule_json", json.dumps([asdict(row) for row in self.schedule]))
        self._set_status("Saved")
