from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from ortools.sat.python import cp_model


def canonical_dj(name: str) -> str:
    """Normalize surrounding whitespace without assuming personal aliases."""
    return str(name).strip()


def parse_clock(value: str) -> float:
    if value is None:
        raise ValueError("Time cannot be empty")
    s = str(value).strip().lower().replace("h", ":")
    parts = [p for p in s.split(":") if p != ""]
    if len(parts) not in (2, 3):
        raise ValueError(f"Invalid time: {value!r}")
    h, m = int(parts[0]), int(parts[1])
    sec = int(parts[2]) if len(parts) == 3 else 0
    if not (0 <= h <= 23 and 0 <= m <= 59 and 0 <= sec <= 59):
        raise ValueError(f"Invalid time: {value!r}")
    return h * 60 + m + sec / 60.0


def fmt_clock(abs_minutes: float) -> str:
    total_seconds = int(round(abs_minutes * 60)) % (24 * 3600)
    h, rem = divmod(total_seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}" if s == 0 else f"{h:02d}:{m:02d}:{s:02d}"


def party_interval(start: str, end: str) -> Tuple[float, float]:
    s = parse_clock(start)
    e = parse_clock(end)
    if e <= s:
        e += 1440.0
    return s, e


def clock_to_party_abs(
    clock: Optional[str], start_abs: float, end_abs: float, prefer: str
) -> Optional[float]:
    if clock is None or str(clock).strip() == "":
        return None
    c = parse_clock(clock)
    candidates = [c - 1440.0, c, c + 1440.0, c + 2880.0]
    valid = [x for x in candidates if start_abs - 1e-9 <= x <= end_abs + 1e-9]
    if valid:
        return min(valid) if prefer == "min" else max(valid)
    if prefer == "min":
        future = [x for x in candidates if x >= start_abs - 1e-9]
        return min(future) if future else max(candidates)
    past = [x for x in candidates if x <= end_abs + 1e-9]
    return max(past) if past else min(candidates)


@dataclass
class DJConstraint:
    name: str
    present: bool = True
    min_time: Optional[str] = None
    max_time: Optional[str] = None


@dataclass
class HistorySet:
    party_id: str
    party_name: str
    date: str
    dj: str
    start: str
    end: str
    value: float = 0.0
    position: Optional[float] = None


@dataclass
class ScheduleRow:
    slot_index: int
    start_abs: float
    end_abs: float
    dj: str
    slot_value: float
    locked: bool = False

    @property
    def start(self) -> str:
        return fmt_clock(self.start_abs)

    @property
    def end(self) -> str:
        return fmt_clock(self.end_abs)


def build_slots(start: str, end: str, n: int, quantum: int = 15):
    """Build slots using quarter-hour rounding where possible."""
    if quantum <= 0:
        raise ValueError("Time increment must be positive.")
    if n <= 0:
        raise ValueError("No DJs are marked as present.")
    s, e = party_interval(start, end)
    total = e - s
    if n == 1:
        return s, e, [(s, e)]

    avg = total / n
    lower = max(quantum, int(avg // quantum) * quantum)
    upper = lower if abs(avg - lower) < 1e-9 else lower + quantum
    standard = upper if (avg - lower) >= (upper - avg) else lower

    # Round down if rounding up leaves no time for the final DJ.
    if (n - 1) * standard >= total:
        standard = lower

    # For very short events, fall back to equal fractional durations.
    if standard <= 0 or (n - 1) * standard >= total:
        duration = total / n
        return s, e, [(s + i * duration, s + (i + 1) * duration) for i in range(n)]

    slots = []
    cursor = s
    for _ in range(n - 1):
        slots.append((cursor, cursor + standard))
        cursor += standard
    slots.append((cursor, e))
    return s, e, slots


def score_slot(start_abs: float, end_abs: float, bands: List[Tuple[str, str, float]]) -> float:
    duration = end_abs - start_abs
    if duration <= 0:
        return 0.0
    total = 0.0
    for bstart, bend, value in bands:
        bs = parse_clock(bstart)
        be = parse_clock(bend)
        if be <= bs:
            be += 1440.0
        for shift in (-1440.0, 0.0, 1440.0, 2880.0):
            a, b = bs + shift, be + shift
            overlap = max(0.0, min(end_abs, b) - max(start_abs, a))
            total += overlap * float(value)
    return total / duration


def _windows(start: str, end: str, constraints: List[DJConstraint]):
    party_start, party_end = party_interval(start, end)
    result = {}
    for c in constraints:
        if not c.present:
            continue
        name = canonical_dj(c.name)
        mn = clock_to_party_abs(c.min_time, party_start, party_end, "min")
        mx = clock_to_party_abs(c.max_time, party_start, party_end, "max")
        mn = party_start if mn is None else max(mn, party_start)
        mx = party_end if mx is None else min(mx, party_end)
        if mx < mn - 1e-9:
            raise ValueError(f"Invalid availability window for {name}: {c.min_time} → {c.max_time}")
        result[name] = (mn, mx)
    return party_start, party_end, result


def validate_schedule(
    start: str, end: str, constraints: List[DJConstraint], schedule: List[ScheduleRow]
) -> List[str]:
    """Return human-readable hard-constraint violations."""
    try:
        party_start, party_end, windows = _windows(start, end, constraints)
    except ValueError as exc:
        return [str(exc)]
    present = {canonical_dj(c.name) for c in constraints if c.present}
    errors = []

    if not schedule:
        return ["No schedule to validate."]
    expected = build_slots(start, end, len(present))[2] if present else []
    if len(schedule) != len(expected):
        errors.append("The slot count does not match the number of present DJs.")
    for i, row in enumerate(schedule):
        if row.slot_index != i:
            errors.append("Invalid slot indices.")
        if row.end_abs <= row.start_abs:
            errors.append("A slot has a zero or negative duration.")
        if i < len(expected):
            a, b = expected[i]
            if abs(row.start_abs - a) > 1e-7 or abs(row.end_abs - b) > 1e-7:
                errors.append("The slots no longer match the event times.")

    scheduled = [canonical_dj(r.dj) for r in schedule]
    if set(scheduled) != present or len(scheduled) != len(present):
        missing = sorted(present - set(scheduled))
        extra = sorted(set(scheduled) - present)
        if missing:
            errors.append("DJs missing from the schedule: " + ", ".join(missing))
        if extra:
            errors.append("Unexpected DJs in the schedule: " + ", ".join(extra))
        if len(scheduled) != len(set(scheduled)):
            errors.append("A DJ is scheduled more than once.")

    for r in schedule:
        dj = canonical_dj(r.dj)
        if dj not in windows:
            continue
        mn, mx = windows[dj]
        if r.start_abs < mn - 1e-7:
            errors.append(
                f"{dj}: starts at {r.start}, before their availability ({fmt_clock(mn)})."
            )
        if r.end_abs > mx + 1e-7:
            errors.append(
                f"{dj}: finishes at {r.end}, after their availability ends ({fmt_clock(mx)})."
            )
    return errors


def _history_duration_minutes(start: str, end: str) -> float:
    try:
        s = parse_clock(start)
        e = parse_clock(end)
        if e <= s:
            e += 1440.0
        return max(0.0, e - s)
    except Exception:
        return 0.0


def history_stats(history: List[HistorySet]):
    stats = {}
    for h in history:
        dj = canonical_dj(h.dj)
        s = stats.setdefault(
            dj, {"sets": 0, "value_sum": 0.0, "minutes_sum": 0.0, "positions": [], "latest": ""}
        )
        s["sets"] += 1
        s["value_sum"] += float(h.value or 0.0)
        s["minutes_sum"] += _history_duration_minutes(h.start, h.end)
        if h.position is not None:
            s["positions"].append(float(h.position))
        if h.date and h.date > s["latest"]:
            s["latest"] = h.date

    for dj, s in stats.items():
        s["avg_value"] = s["value_sum"] / s["sets"] if s["sets"] else 0.0
        s["avg_minutes"] = s["minutes_sum"] / s["sets"] if s["sets"] else 0.0
        s["avg_position"] = sum(s["positions"]) / len(s["positions"]) if s["positions"] else None
    return stats


def solve_schedule(
    start: str,
    end: str,
    constraints: List[DJConstraint],
    bands: List[Tuple[str, str, float]],
    history: Optional[List[HistorySet]] = None,
    locks: Optional[Dict[int, str]] = None,
) -> List[ScheduleRow]:
    history = history or []
    locks = {int(k): canonical_dj(v) for k, v in (locks or {}).items()}

    present_constraints = [
        DJConstraint(canonical_dj(c.name), True, c.min_time, c.max_time)
        for c in constraints
        if c.present
    ]
    names = [c.name for c in present_constraints]
    if any(not name for name in names):
        raise ValueError("DJ name cannot be empty.")
    if len(names) != len(set(names)):
        raise ValueError("A DJ appears more than once in the availability list.")

    party_start, party_end, slots = build_slots(start, end, len(names))
    _, _, windows = _windows(start, end, present_constraints)
    slot_values = [score_slot(a, b, bands) for a, b in slots]

    model = cp_model.CpModel()
    x = {}
    feasible_map = {}

    for i, (a, b) in enumerate(slots):
        for dj in names:
            mn, mx = windows[dj]
            feasible = a >= mn - 1e-7 and b <= mx + 1e-7
            feasible_map[i, dj] = feasible
            var = model.NewBoolVar(f"x_{i}_{dj}")
            x[i, dj] = var
            if not feasible:
                model.Add(var == 0)

    for i in range(len(slots)):
        model.Add(sum(x[i, dj] for dj in names) == 1)
    for dj in names:
        model.Add(sum(x[i, dj] for i in range(len(slots))) == 1)

    for i, dj in locks.items():
        if i < 0 or i >= len(slots):
            raise ValueError(f"Invalid lock on slot {i + 1}.")
        if dj not in names:
            raise ValueError(f"Invalid lock: {dj} is not present.")
        if not feasible_map[i, dj]:
            a, b = slots[i]
            raise ValueError(
                f"Invalid lock: {dj} cannot play during {fmt_clock(a)}–{fmt_clock(b)}."
            )
        model.Add(x[i, dj] == 1)

    stats = history_stats(history)
    hist_avgs = [s["avg_value"] for s in stats.values() if s["sets"]]
    global_avg = sum(hist_avgs) / len(hist_avgs) if hist_avgs else 0.0
    hist_minutes = [s["minutes_sum"] for s in stats.values() if s["sets"]]
    global_minutes = sum(hist_minutes) / len(hist_minutes) if hist_minutes else 0.0

    objective_terms = []
    n = len(slots)
    for i in range(n):
        rel_pos = 0.5 if n == 1 else i / (n - 1)
        slot_minutes = slots[i][1] - slots[i][0]
        for dj in names:
            s = stats.get(dj)
            avg_value = s["avg_value"] if s else global_avg
            deficit = global_avg - avg_value
            value_fairness_reward = slot_values[i] * deficit * 120.0

            dj_minutes = s["minutes_sum"] if s else global_minutes
            minutes_deficit = global_minutes - dj_minutes
            duration_fairness_reward = slot_minutes * minutes_deficit * 0.08

            repeat_penalty = 0.0
            if s and s["positions"]:
                nearest = min(abs(rel_pos - p) for p in s["positions"])
                repeat_penalty = max(0.0, 0.28 - nearest) * 75.0

            tie_break = -(names.index(dj) + 1) * (i + 1) * 0.0001
            coef = int(
                round(
                    (value_fairness_reward + duration_fairness_reward - repeat_penalty + tie_break)
                    * 1000
                )
            )
            objective_terms.append(coef * x[i, dj])

    model.Maximize(sum(objective_terms))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 8.0
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)

    if status == cp_model.UNKNOWN:
        raise RuntimeError("Search timed out without a solution. Please try again.")
    if status == cp_model.MODEL_INVALID:
        raise ValueError("Invalid model: check the time-band values and history.")
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        diagnostics = []
        for dj in names:
            possible = [i + 1 for i in range(len(slots)) if feasible_map[i, dj]]
            diagnostics.append(f"{dj}: available slots = {possible or 'none'}")
        raise RuntimeError(
            "No feasible schedule satisfies the hard constraints.\n\n" + "\n".join(diagnostics)
        )

    result = []
    for i, (a, b) in enumerate(slots):
        dj = next(d for d in names if solver.Value(x[i, d]))
        result.append(
            ScheduleRow(
                slot_index=i,
                start_abs=a,
                end_abs=b,
                dj=dj,
                slot_value=slot_values[i],
                locked=i in locks,
            )
        )
    return result
