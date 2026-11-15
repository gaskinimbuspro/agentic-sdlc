import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from backend_standard.dispatch import DispatchLedger, Operation
from backend_standard.gates import Rejected


@pytest.fixture
def clocks():
    return [1000.0]


def setup_ledger(tmp_path, clocks):
    ledger = DispatchLedger(tmp_path / "ledger.sqlite", clock=lambda: clocks[0])
    ledger.register("task-01", "a" * 64, attempt_budget=2, lease_seconds=20)
    return ledger


def test_claim_is_exclusive_across_concurrent_connections(tmp_path, clocks):
    ledger = setup_ledger(tmp_path, clocks)
    barrier = threading.Barrier(2, timeout=5)

    def attempt(worker):
        barrier.wait()
        try:
            return ledger.claim("task-01", worker, f"{worker}-request")
        except Rejected as error:
            return str(error)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, ("alice", "bob")))
    winner = next(result for result in results if not isinstance(result, str))
    assert results.count("Task already has an active owner") == 1
    retry = DispatchLedger(ledger.path, clock=lambda: clocks[0])
    assert retry.claim("task-01", winner.worker, f"{winner.worker}-request") == winner


def test_restart_expiry_and_fencing(tmp_path, clocks):
    ledger = setup_ledger(tmp_path, clocks)
    old = ledger.claim("task-01", "alice", "first")
    clocks[0] = old.expires_at
    restarted = DispatchLedger(ledger.path, clock=lambda: clocks[0])
    with pytest.raises(Rejected, match="Claim request has expired"):
        restarted.claim("task-01", "alice", "first")
    new = restarted.claim("task-01", "bob", "second")
    assert new.attempt == 2
    assert new.token != old.token
    with pytest.raises(Rejected, match="Stale or expired"):
        ledger.submit("task-01", old.token, "b" * 40)
    clocks[0] = new.expires_at
    with pytest.raises(Rejected, match="Attempt budget exhausted"):
        ledger.claim("task-01", "cam", "third")


def test_candidate_is_staged_and_cannot_be_replaced(tmp_path, clocks):
    ledger = setup_ledger(tmp_path, clocks)
    active = ledger.claim("task-01", "alice", "first")
    ledger.submit("task-01", active.token, "b" * 40)
    ledger.submit("task-01", active.token, "b" * 40)
    with pytest.raises(Rejected, match="already staged"):
        ledger.submit("task-01", active.token, "c" * 40)
    with pytest.raises(Rejected, match="candidate for review"):
        ledger.claim("task-01", "bob", "second")


def test_ready_packet_cannot_be_replaced(tmp_path, clocks):
    ledger = setup_ledger(tmp_path, clocks)
    ledger.register("task-01", "a" * 64, attempt_budget=2, lease_seconds=20)
    with pytest.raises(Rejected, match="conflicts with the protected packet"):
        ledger.register("task-01", "b" * 64, attempt_budget=2, lease_seconds=20)


def test_uncertain_external_write_reconciles_across_restart(tmp_path, clocks):
    ledger = setup_ledger(tmp_path, clocks)
    intent = "e" * 64
    key = "repo:project-01"
    external_resources = []

    def provision(active_ledger):
        operation = active_ledger.reserve(key, intent)
        if operation.state == "reserved":
            external_resources.append("github:100")
            raise TimeoutError(
                "The provider created the resource before losing its response"
            )
        if operation.state == "reconcile":
            assert len(external_resources) == 1
            active_ledger.observe(key, intent, external_resources[0])
        return active_ledger.reserve(key, intent)

    with pytest.raises(TimeoutError):
        provision(ledger)
    restarted = DispatchLedger(ledger.path, clock=lambda: clocks[0])
    assert restarted.reserve(key, intent) == Operation("reconcile", None)
    assert provision(restarted) == Operation("observed", "github:100")
    assert provision(ledger) == Operation("observed", "github:100")
    restarted.observe(key, intent, "github:100")
    assert external_resources == ["github:100"]
    with pytest.raises(Rejected, match="Conflicting"):
        ledger.reserve(key, "f" * 64)
    with pytest.raises(Rejected, match="Receipt does not match"):
        ledger.observe(key, intent, "github:101")
