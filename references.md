# References

The sources behind the metric, formula and event documents. Only current, supported Kubernetes versions are used. Every entry says how it was checked, so a claim can be traced to the text it came from.

## Version scope

Checked on 2026-10-29 against [kubernetes.io/releases](https://kubernetes.io/releases/) and [patch releases](https://kubernetes.io/releases/patch-releases/).

| Minor | Latest patch | End of life | Status on 2026-10-29 | Used here |
|---|---|---|---|---|
| 1.37 | 1.37.1 | 2027-10-28 | Latest, supported | Yes: primary |
| 1.36 | 1.36.5 | 2027-06-28 | Supported | Yes |
| 1.35 | 1.35.9 | 2027-02-28 | Supported | Yes: VKS cluster in the lab |
| 1.34 | 1.34.12 | 2026-10-27 | End of life two days ago | No |
| 1.33 and older | — | 2026-06-28 and earlier | End of life | No |
| 1.32 | 1.32.13 | 2026-02-28 | End of life | No. **The lab Supervisor runs 1.32**, so Supervisor behaviour in the lab is on an unsupported version |

The release page's support rule text ("most recent three minor releases") disagrees with its table, which still lists 1.34 as supported until 2026-10-27. Today is after that date, so 1.34 is excluded either way.

## Upstream Kubernetes docs

Read from the source files in the `kubernetes/website` repository, branch `dev-1.37` for 1.37 (the 1.37 release branch does not exist yet in that repo) and `release-1.35` for 1.35. Commits: `dev-1.37` at `aebe074`, `release-1.35` at `8817d35`. "Read" means the full text was checked with grep or sed, not a summary.

| Topic | Source | Version | How checked | What it gives |
|---|---|---|---|---|
| Node heartbeats, node controller | [concepts/architecture/nodes](https://kubernetes.io/docs/concepts/architecture/nodes/) | 1.37 | Read | Leases in `kube-node-lease`; controller sets Ready to Unknown; 5 min before the first eviction request; check every 5 s (`--node-monitor-period`); eviction rate 0.1/s |
| Leases | [concepts/architecture/leases](https://kubernetes.io/docs/concepts/architecture/leases/) | 1.37 | Read | Each heartbeat updates `spec.renewTime` of the node's Lease |
| Node status and Ready condition | [reference/node/node-status](https://kubernetes.io/docs/reference/node/node-status/) | 1.37 | Read | Ready is Unknown when the controller has not heard from the node within `node-monitor-grace-period` (default 50 s) |
| Node-pressure eviction | [concepts/scheduling-eviction/node-pressure-eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/) | 1.37 | Read | Eviction signal definitions; default hard thresholds: `memory.available<100Mi` (Linux), `nodefs.available<10%`, `imagefs.available<15%`, `nodefs.inodesFree<5%`, `imagefs.inodesFree<5%`; pressure conditions map to signals; memory available excludes `inactive_file` |
| Taints and tolerations | [concepts/scheduling-eviction/taint-and-toleration](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/) | 1.37 | Read (grep) | `node.kubernetes.io/not-ready` and `node.kubernetes.io/unreachable` taints |
| Pod phases | [concepts/workloads/pods/pod-lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) | 1.37 | Read | `Pending`, `Running`, `Succeeded`, `Failed`, `Unknown`. A node that dies sets its Pods to `Failed` |
| CPU limit and OOM | [concepts/configuration/manage-resources-containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) | 1.37 | Read | CPU limit is a hard limit enforced by throttling; memory limit is enforced by OOM kill, reactively; `OOMKilled` reason; `100m` = one hundred millicpu |
| Deployment progress | [concepts/workloads/controllers/deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) | 1.37 | Read (grep) | `Progressing` condition with reason `ProgressDeadlineExceeded` |
| Resource quotas | [concepts/policy/resource-quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/) | 1.37 | Read (grep) | `requests.storage` and `<storage-class>.storageclass.storage.k8s.io/requests.storage` |
| PSI concepts | [reference/instrumentation/understand-psi-metrics](https://kubernetes.io/docs/reference/instrumentation/understand-psi-metrics/) | 1.37 | Read | `some` and `full` definitions; `avg10/60/300` as percentages of wall-clock time; `total` in microseconds; kernel 4.20+, cgroup v2, `psi=1` on some distributions |
| PSI status | [reference/instrumentation/node-metrics](https://kubernetes.io/docs/reference/instrumentation/node-metrics/) | 1.37 | Read | `KubeletPSI` stable; locked to true from 1.36 |
| PSI Prometheus names | [concepts/cluster-administration/system-metrics](https://kubernetes.io/docs/concepts/cluster-administration/system-metrics/) | 1.37 | Read (grep) | Six counters: `container_pressure_{cpu,memory,io}_{stalled,waiting}_seconds_total` |
| kubelet evictions | `pkg/kubelet/metrics/metrics.go` in [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes) | 1.35.9 (tag `v1.35.9`) | Read in source | `kubelet_evictions` counter, label by eviction signal |
| Kubelet event reasons | `pkg/kubelet/events/event.go` | 1.35.9 | Read in source | `Killing`, `BackOff`, `NodeNotReady`, `NodeReady`, `FailedMount`, `Unhealthy`. **No `OOMKilling` or `SystemOOM` constant** |
| Eviction event and pod reason | `pkg/kubelet/eviction/eviction_manager.go`, `helpers.go` | 1.35.9 | Read in source | Node event `EvictionThresholdMet`; evicted pod gets reason `Evicted` |
| Event retention | [kube-apiserver reference](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-apiserver/) | 1.37 and 1.35 | Read | `--event-ttl` default `1h0m0s` |
| Controller-manager defaults | [kube-controller-manager reference](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-controller-manager/) | 1.37 and 1.35 | Read | `--node-monitor-grace-period` default `50s` |
| API server toleration defaults | [kube-apiserver reference](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-apiserver/) | 1.37 | Read | `--default-not-ready-toleration-seconds` and `--default-unreachable-toleration-seconds`, default 300 |

## Linux kernel

| Topic | Source | How checked | What it gives |
|---|---|---|---|
| CFS bandwidth | [scheduler/sched-bwc](https://www.kernel.org/doc/html/latest/scheduler/sched-bwc.html) | Read (summary) | `cpu.cfs_period_us` default 100 ms; `nr_periods`, `nr_throttled`, `throttled_time` |
| PSI | [accounting/psi](https://docs.kernel.org/accounting/psi.html) | Linked from Kubernetes; not read directly | Definitions behind `some` and `full` |

## Prometheus rules (kubernetes-mixin)

Pinned to commit `ea8e318` (HEAD on 2026-10-29). Alert expressions are not tied to one Kubernetes version. Some files were read only as summaries, because the fetch tool truncates long expressions.

| Alert | File | How checked | Used in |
|---|---|---|---|
| `CPUThrottlingHigh` (> 25 %, 15 min) | `alerts/resource_alerts.libsonnet` | Summary | [metrics-contention.md](metrics-contention.md) |
| `KubeCPUOvercommit`, `KubeMemoryOvercommit`, quota alerts | `alerts/resource_alerts.libsonnet` | Summary | contention |
| `KubePodCrashLooping`, `KubePodNotReady`, replica mismatch, `KubeJobFailed` | `alerts/apps_alerts.libsonnet` | Read (fragments) | [metrics-availability.md](metrics-availability.md) |
| `KubeNodeNotReady`, `KubeNodePressure`, `KubeNodeUnreachable`, `KubeNodeReadinessFlapping`, `KubeNodeEviction`, `KubeletPlegDurationHigh`, `KubeletDown` | `alerts/kubelet.libsonnet` | Read | availability, contention |
| Volume filling up | `alerts/storage_alerts.libsonnet` | Summary | [metrics-consumption.md](metrics-consumption.md) |
| `KubeClientErrors` (> 1 % 5xx) | `alerts/system_alerts.libsonnet` | Summary | availability |

## Vendor (Broadcom)

| Topic | Source | How checked | Limit |
|---|---|---|---|
| Supervisor metrics for VCF 9.1 | [Viewing Supervisor Metrics](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/infrastructure-operations/connect-to-data-sources/vsphere-supervisor-monitoring/steps-to-monitor-vsphere-supervisor-clusters-and-resources/vsphere-supervisor-metrics.html) | Fetched (summary of table) | Names and units only, no formulas |
| VKS 3.6 and Cluster API conditions | Lab output (see [properties.md](properties.md)) | Lab | Condition names are as returned by the lab |

Broadcom does not publish formulas for VCF Operations metrics; see [research-notes.md](research-notes.md).

## Sources not used

| Source | Why |
|---|---|
| Kubernetes docs for 1.32 and older | End of life |
| Secondary blogs for node timers (40 s, 30 s) | Contradicted by the primary text (50 s) |
| cAdvisor source | The default branch in the checkout did not include the metric definitions; CFS and OOM names are unverified at source |
