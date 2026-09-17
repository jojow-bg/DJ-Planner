"""Fictional, reproducible demonstration; never replaces an existing database."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

from .data_store import DataStore
from .planner_core import HistorySet, build_slots, fmt_clock, score_slot


def seed_demo(path: Path) -> None:
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"Refusing to replace an existing database: {path}")
    data = json.loads(files("dj_planner").joinpath("data/demo.json").read_text(encoding="utf-8"))
    store = DataStore(path)
    try:
        store.replace_djs(data["roster"])
        store.replace_bands(data["bands"])
        history = []
        for event in data["past_events"]:
            names = event["order"]
            slots = build_slots("20:00", "02:00", len(names))[2]
            for i, (name, (a, b)) in enumerate(zip(names, slots)):
                history.append(
                    HistorySet(
                        event["id"],
                        event["name"],
                        event["date"],
                        name,
                        fmt_clock(a),
                        fmt_clock(b),
                        score_slot(a, b, data["bands"]),
                        i / (len(names) - 1),
                    )
                )
        store.replace_history(history)
        for key, value in data["event"].items():
            store.set_setting("party_" + key, value)
        store.set_setting("constraints_json", json.dumps(data["constraints"]))
        store.set_setting("initialized", "1")
    finally:
        store.close()
