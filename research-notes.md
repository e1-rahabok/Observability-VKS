# Research Notes and Open Doubts

Working notes for the formula and contention, consumption and availability documents. The full reference list, with versions and how each source was read, is in [references.md](references.md). Nothing here was checked against the lab: the lab was not queried.

## Status of the doubts

The first version of these notes had 18 doubts. A second pass read the upstream Kubernetes 1.37 and 1.35 docs and the 1.35.9 kubelet source directly, which closed most of them. Status after that pass:

| # | Topic | Status | What the primary source says |
|---|---|---|---|
| 1 | PSI stability | **Resolved** | 1.35: `KubeletPSI` enabled by default. 1.36 onward: stable, locked to true (1.37 docs) |
| 2 | PSI metric names | **Resolved** | Six counters: `container_pressure_{cpu,memory,io}_{stalled,waiting}_seconds_total` (1.37 system-metrics) |
| 3 | CPU throttle alert expression | Open | Only a summary read; the exact PromQL was not quoted in full |
| 4 | Memory working set and OOM | Open | Kubernetes says the working set includes some cached memory and that the kernel enforces memory limits reactively. Whether the OOM killer uses this metric is not stated in the docs |
| 5 | Eviction default thresholds | **Resolved** | `memory.available<100Mi` (Linux), `nodefs.available<10%`, `imagefs.available<15%`, `nodefs.inodesFree<5%`, `imagefs.inodesFree<5%` (1.37 docs) |
| 6 | Node controller timers | **Resolved, and corrected** | Ready goes Unknown after `node-monitor-grace-period`, default **50 s** (not 40 s as first noted). Eviction starts 5 min after Unknown. Default not-ready and unreachable tolerations are 300 s |
| 7 | Lease renew interval | Open | The Leases page describes the mechanism but not an interval. Not confirmed |
| 8 | `OOMKilling` event | **Resolved: not a kubelet event** | Kubelet 1.35.9 source has no OOM event constant. The container status reason `OOMKilled` is the signal |
| 9 | Event retention | **Resolved** | `kube-apiserver --event-ttl` default `1h0m0s` |
| 10 | Eviction events | **Resolved** | Pod reason and event `Evicted`; node event `EvictionThresholdMet` (1.35.9 source) |
| 11 | VCF Operations formulas | Open | Broadcom publishes names and units but no formulas. Cannot be closed from upstream sources |
| 12 | "Top 95%" meaning | Open | Broadcom KB: a 95th percentile ignores the top 5 % of samples. Over time or over child objects is not stated |
| 13 | VKS metric collection path | Open | Blog only (third-party). Needs Broadcom's VCF 9.1 VKS monitoring doc |
| 14 | Cluster API metric names | Open | Not checked in this pass |
| 15 | Supervisor storage quota formula | Open | `used ÷ appliedLimit` is a derivation, not a Broadcom formula |
| 16 | `container_oom_events_total`, `kubelet_pod_start_duration_seconds`, `container_cpu_usage_seconds_total` | Partly resolved | `kubelet_evictions` confirmed in kubelet source. The three others were not confirmed (cAdvisor and kubelet metric definitions were not in the checked-out source) |
| 17 | Kubelet metric names on system-metrics page | Partly resolved | PSI names confirmed. Volume and eviction names not yet read on that page |
| 18 | Disk I/O (IOPS, bytes/s) | Open | Not in the lab model; cAdvisor filesystem counters not checked |

## Corrections made in this pass

- **Node grace period is 50 s, not 40 s.** Several secondary sources said 40 s. The 1.37 and 1.35 docs say 50 s. The availability diagram and table are updated.
- **No OOM event from the kubelet.** The `OOMKilling` and `SystemOOM` names in the first draft were unverified guesses. The kubelet source has neither. Documents now say OOM is in container status.
- **Eviction defaults are verified.** The first draft cited them as the "example" in the docs. They are the documented defaults.

## Things that conflict with [metrics.md](metrics.md) or the repo rules

- **New source codes.** `PROM`, `VCFO` and `EVT` are added. [CLAUDE.md](CLAUDE.md) asks for the same codes as the existing tables. This is still open for your decision.
- **New metrics are not lab-verified.** Rows marked `PROM` or `VCFO` were not seen in the lab. The notes column says "Not in the lab" where it applies.
- **Supervisor-side formulas.** Formulas for Supervisor metrics are derived from lab field paths, not from a Broadcom formula (rows 11 and 15).
- **Lab Supervisor is on an unsupported Kubernetes version.** Supervisor 1.32 reached end of life on 2026-02-28. The references deliberately exclude 1.32, so Supervisor behaviour in the lab should be read as the behaviour of an end-of-life release.
