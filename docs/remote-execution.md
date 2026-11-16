# Remote execution and Hetzner pilot

This is the operating profile for [pilot issue #7](https://github.com/gaskinimbuspro/agentic-sdlc/issues/7). Start on an explicitly authorized disposable target with synthetic workloads. Record the provider, redacted host identity, architecture, CPU, memory, disk and attachment topology, OS/kernel, cgroups, filesystem, tool versions, allocation and budget. Treat reported host specifications as hypotheses until measured.

## Run order

1. Separate the control service, scoped worker and preview workloads. Keep durable control state off workers and their credentials distinct. Limit CPU, memory, disk and process counts where the target supports them. Keep untrusted public-contribution code out of shared privileged runners. Reserve one coding task and one heavy job for the first trial.
2. Observe idle, cold build/test and warm build/test under representative loads. Record CPU, memory, and I/O pressure, free disk, memory headroom, OOM events, queue depth and control/preview health with consistent intervals. On Linux, collect the `some` pressure line from `/proc/pressure/cpu`, `/proc/pressure/memory` and `/proc/pressure/io`. Record the averaging window and host or cgroup scope. Record the difference between stalls and utilization.
3. Run a real task through local verification, clean candidate-bound CI, independent review, latest-base check, authorized integration and target smoke. Measure queue, implementation, local test, CI, review, integration, smoke and external wait separately. Record total accepted-task cost and repair rounds with their units.
4. Run the recovery experiments below. Exercise the chosen SDK/CLI, actual provider authentication and permissions, safe rate-limit handling, usage/cost accounting and credential revocation.
5. Observe at least 24 hours with sampled idle and workload periods. Select window, cadence and resource/stop thresholds before the run. Record an elapsed failure or missing sample as an operational finding. Run destructive fault injection separately from the qualifying healthy window.
6. Restore protected control-state backups and essential configuration to a separately authorized host or recovery environment. Verify stored claims and receipts, fence old workers, and validate the restored service against the selected recovery objectives. Measure elapsed recovery and data loss. Hetzner server backups and snapshots omit attached Volumes. Include their data in a separately tested recovery path where applicable.
7. Compare concurrency one and two after the serial run is reliable. Record sample sizes, phase times, pressure peaks, cost and defects under comparable workloads. Obtain review of capacity, topology, cost bounds and the integration policy before increasing concurrency. Initial live pilot integration requires the authority specified in issue #7.

Useful read-only probes include `uname -m`, `nproc`, `free -b`, `df -P` for the actual workspace mount and the pressure files above. Prefer redacted exports and numeric metrics over complete provider inventory, shell history or environment variables.

## Recovery and rejection experiments

| Case | Injected condition and expected observation |
| --- | --- |
| O01 | Race two claims and verify one active owner and one rejected claim. |
| O02 | Kill/restart the worker. Verify expiry and reject its stale submission. |
| O03 | Restart the coordinator after reserving a provider write. Recover or safely block through authoritative readback. |
| O04 | Move the integration base. Reject old CI and review receipts. |
| O05 | Supply a missing, failed, empty or skipped required report. Block the transition. |
| O06 | Supply self-issued or forged evidence. Confirm protected-source and reviewer checks reject it. |
| O07 | Interrupt implementation mid-task. Restore from the scoped handoff and verify version and workspace boundaries. |
| O08 | Exhaust wall time, attempts or cost. Verify the owned blocked state and absence of automatic retries. |
| O09 | Saturate the worker lane within approved bounds. Verify the control and preview health thresholds and load-shedding decision. |
| O10 | Exercise a provider limit or permission failure. Verify bounded recovery and no privilege substitution. |
| O11 | Fail target smoke during otherwise healthy rollout. Verify promotion stops and observe recovery. |
| O12 | Restore on a separate target and attempt an operation from the old coordinator. Verify single active authority and reconciled receipts. |

## Report checklist

| Case | Required observation |
| --- | --- |
| RP01 | Verified host inventory and redacted idle, cold and warm resource observations. |
| RP02 | Control/worker/preview isolation and one end-to-end task with independent review and separate phase durations. |
| RP03 | Actual toolchain and provider permission, quota and usage/cost results. |
| RP04 | A qualifying soak record with idle and working service observations. |
| RP05 | Off-host restoration, verified recovered state, observed recovery time and data-loss interval. |
| RP06 | Comparable one- and two-task samples and reviewed capacity, budget, topology and integration decision. |

The remote adoption report contains O01–O12 and RP01–RP06.

## Soak record

Approve a `remote_window` in the protected policy before starting. Set `not_before` and `not_after` to the bounds of the approved run in integer Unix seconds in UTC and set positive `minimum_idle_seconds` and `minimum_workload_seconds`. Allow enough time for observing the measured window and sampling cadence inside the approved bounds.

Put a `soak` object in the protected remote report. Use actual UTC Unix seconds for `started_at`, `ended_at` and each `samples[].at`, with both endpoints in order. The measured window must finish by the verifier's clock, fit inside the approved run and span at least 86,400 seconds. The reference profile allows positive gaps of at most 300 seconds.

Each sample records `activity` of `idle` or `workload`, a `service` result of `healthy` for the qualifying window, and `pressure` containing numeric `cpu_some_pct`, `memory_some_pct` and `io_some_pct` (0–100). Demonstrate each required activity duration with consecutive samples of that activity. A single observation supplies no duration. Use the same documented window and scope for pressure measurements. Preserve raw observations or a protected reference for each case and review resource objectives separately.

Primary sources. [Linux pressure stall information](https://docs.kernel.org/accounting/psi.html) · [Hetzner backups and snapshots](https://docs.hetzner.com/cloud/servers/backups-snapshots/overview/) · [PostgreSQL backup and restore](https://www.postgresql.org/docs/18/backup.html)
