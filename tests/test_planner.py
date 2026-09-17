from dataclasses import replace

import pytest

from dj_planner.planner_core import (
    DJConstraint,
    HistorySet,
    build_slots,
    fmt_clock,
    history_stats,
    parse_clock,
    score_slot,
    solve_schedule,
    validate_schedule,
)


def test_every_present_dj_has_exactly_one_contiguous_slot():
    constraints = [DJConstraint(n) for n in ["Nova", "Pulse", "Echo"]]
    constraints += [DJConstraint("Flux", present=False)]
    rows = solve_schedule("20:00", "23:00", constraints, [])
    assert {r.dj for r in rows} == {"Nova", "Pulse", "Echo"}
    assert len(rows) == 3
    assert [r.slot_index for r in rows] == [0, 1, 2]
    assert [(r.start, r.end) for r in rows] == [
        ("20:00", "21:00"),
        ("21:00", "22:00"),
        ("22:00", "23:00"),
    ]
    assert validate_schedule("20:00", "23:00", constraints, rows) == []


def test_availability_crossing_midnight_and_lock():
    cs = [
        DJConstraint("Nova", min_time="00:00"),
        DJConstraint("Pulse", max_time="00:00"),
        DJConstraint("Echo"),
    ]
    rows = solve_schedule("23:00", "02:00", cs, [], locks={2: "Nova"})
    assert [r.dj for r in rows] == ["Pulse", "Echo", "Nova"]
    assert rows[2].locked
    assert validate_schedule("23:00", "02:00", cs, rows) == []


def test_collectively_infeasible_even_when_every_dj_has_a_possible_slot():
    cs = [DJConstraint("Nova", max_time="21:00"), DJConstraint("Pulse", max_time="21:00")]
    with pytest.raises(RuntimeError, match="No feasible schedule"):
        solve_schedule("20:00", "22:00", cs, [])


@pytest.mark.parametrize("locks", [{2: "Nova"}, {0: "Missing"}, {0: "Nova", 1: "Nova"}])
def test_invalid_or_conflicting_locks(locks):
    with pytest.raises((ValueError, RuntimeError)):
        solve_schedule(
            "20:00", "22:00", [DJConstraint("Nova"), DJConstraint("Pulse")], [], locks=locks
        )


def test_lock_cannot_override_availability():
    with pytest.raises(ValueError, match="Invalid lock"):
        solve_schedule(
            "20:00",
            "22:00",
            [DJConstraint("Nova", min_time="21:00"), DJConstraint("Pulse")],
            [],
            locks={0: "Nova"},
        )


@pytest.mark.parametrize(
    "cs",
    [
        [],
        [DJConstraint("Nova", False)],
        [DJConstraint("Nova"), DJConstraint(" Nova ")],
        [DJConstraint(" ")],
    ],
)
def test_empty_absent_or_duplicate_roster_rejected(cs):
    with pytest.raises(ValueError):
        solve_schedule("20:00", "22:00", cs, [])


def test_impossible_window():
    with pytest.raises(ValueError, match="Invalid availability window"):
        solve_schedule(
            "20:00", "23:00", [DJConstraint("Nova", min_time="22:00", max_time="21:00")], []
        )


def test_quarter_hour_rounding_and_final_remainder():
    a, b, slots = build_slots("20:00", "00:00", 5)
    assert (a, b) == (1200, 1440)
    assert [end - start for start, end in slots] == [45, 45, 45, 45, 60]
    assert all(start % 15 == 0 and end % 15 == 0 for start, end in slots)


def test_short_events_keep_legacy_equal_split_fallback():
    _, _, slots = build_slots("20:00", "20:10", 3)
    assert sum(b - a for a, b in slots) == pytest.approx(10)
    assert all(b > a for a, b in slots)


def test_validation_detects_duplicate_unavailable_and_stale_slots():
    cs = [DJConstraint("Nova"), DJConstraint("Pulse")]
    rows = solve_schedule("20:00", "22:00", cs, [])
    assert validate_schedule("20:00", "22:00", cs, [rows[0], replace(rows[1], dj=rows[0].dj)])
    assert validate_schedule("20:00", "22:00", cs, [replace(rows[0], dj="Flux"), rows[1]])
    assert validate_schedule("20:00", "23:00", cs, rows)
    assert validate_schedule(
        "20:00", "22:00", cs, [replace(rows[0], end_abs=rows[0].start_abs), rows[1]]
    )
    assert validate_schedule("20:00", "22:00", cs, [])


def test_weighted_band_score_across_midnight():
    assert (
        score_slot(23 * 60 + 30, 24 * 60 + 30, [("23:00", "00:00", 2), ("00:00", "01:00", 4)]) == 3
    )


def hist(name, value=0, position=None, start="20:00", end="21:00"):
    return HistorySet("DEMO", "Demo", "2026-01-01", name, start, end, value, position)


def test_value_deficit_rewards_previously_disadvantaged_dj():
    rows = solve_schedule(
        "20:00",
        "22:00",
        [DJConstraint("Nova"), DJConstraint("Pulse")],
        [("20:00", "21:00", 1), ("21:00", "22:00", 5)],
        [hist("Nova", 1), hist("Pulse", 5)],
    )
    assert rows[1].dj == "Nova"


def test_position_rotation_avoids_previous_positions_when_possible():
    rows = solve_schedule(
        "20:00",
        "22:00",
        [DJConstraint("Nova"), DJConstraint("Pulse")],
        [],
        [hist("Nova", position=0), hist("Pulse", position=1)],
    )
    assert [r.dj for r in rows] == ["Pulse", "Nova"]


def test_longer_remainder_favors_lower_accumulated_minutes():
    names = ["Nova", "Pulse", "Echo", "Orbit", "Prism"]
    history = [hist(n, end="20:15" if n == "Nova" else "22:00") for n in names]
    rows = solve_schedule("20:00", "00:00", [DJConstraint(n) for n in names], [], history)
    assert rows[-1].dj == "Nova"


def test_hard_constraints_take_priority_over_rotation():
    rows = solve_schedule(
        "20:00",
        "22:00",
        [DJConstraint("Nova", max_time="21:00"), DJConstraint("Pulse")],
        [],
        [hist("Nova", position=0), hist("Pulse", position=1)],
    )
    assert rows[0].dj == "Nova"


def test_history_tracks_midnight_duration():
    stats = history_stats([hist("Nova", value=3, position=0.5, start="23:30", end="00:30")])["Nova"]
    assert stats["minutes_sum"] == 60
    assert stats["avg_position"] == 0.5
    assert stats["avg_value"] == 3


@pytest.mark.parametrize("clock", ["24:00", "20:60", "bad", "", None])
def test_invalid_clocks(clock):
    with pytest.raises(ValueError):
        parse_clock(clock)


def test_clock_formats():
    assert parse_clock("20h15") == 1215
    assert fmt_clock(25 * 60 + 30) == "01:30"
