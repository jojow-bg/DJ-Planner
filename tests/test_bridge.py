from dj_planner.bridge import DJPlannerBridge
from dj_planner.demo import seed_demo


def test_fresh_start_empty_roster_stays_empty(app, tmp_path):
    path = tmp_path / "planner.sqlite3"
    bridge = DJPlannerBridge(path)
    assert bridge.roster == []
    bridge.addDJ("Nova")
    bridge.removeDJ(0)
    bridge.bands = []
    bridge.saveState()
    bridge.store.close()
    reopened = DJPlannerBridge(path)
    assert reopened.roster == []
    assert reopened.bands == []
    reopened.store.close()


def test_manual_schedule_and_locks_survive_restart(app, tmp_path):
    path = tmp_path / "demo.sqlite3"
    seed_demo(path)
    bridge = DJPlannerBridge(path)
    bridge.generate()
    assert len(bridge.schedule) == 6
    bridge.swapSlots(0, 1)
    bridge.toggleLock(2)
    expected = [(r.dj, r.locked) for r in bridge.schedule]
    bridge.store.close()
    reopened = DJPlannerBridge(path)
    assert [(r.dj, r.locked) for r in reopened.schedule] == expected
    assert reopened.locks == {2: expected[2][0]}
    reopened.store.close()


def test_invalid_manual_edit_cannot_be_archived(app, tmp_path):
    path = tmp_path / "demo.sqlite3"
    seed_demo(path)
    bridge = DJPlannerBridge(path)
    bridge.generate()
    errors = []
    bridge.errorRaised.connect(errors.append)
    nova = next(i for i, r in enumerate(bridge.schedule) if r.dj == "Nova")
    bridge.swapSlots(0, nova)
    assert errors
    count = len(bridge.history)
    bridge.archiveCurrent()
    assert len(bridge.history) == count
    bridge.store.close()
