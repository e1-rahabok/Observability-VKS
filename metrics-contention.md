# VKS Contention Metrics

Contention metrics show that work is waiting for a resource, or that a limit has been hit. A busy resource can still be healthy; contention means demand is being refused or delayed. Examples: throttled, out of memory, queue, dropped, outstanding, latency.

Grouped by object type, in the same order as [README.md](README.md). Formulas are in [metrics-formulas.md](metrics-formulas.md). Consumption (how much is used) is in [metrics-consumption.md](metrics-consumption.md), and failures and events are in [metrics-availability.md](metrics-availability.md).

Source codes are those of [metrics.md](metrics.md), plus `PROM` and `VCFO` (see the note in [metrics-formulas.md](metrics-formulas.md#source-codes)). `Lab` means the field was returned by the lab; otherwise it is from the upstream docs.

## Contention types

| Type | What it means | Main signal |
|---|---|---|
| Throttled | A CPU limit stopped the container from running | CFS throttle ratio, PSI CPU `some` |
| Out of memory | Memory limit or node memory exhausted | OOM events, `OOMKilled`, eviction signal |
| Queue | Work is waiting in a queue | Workqueue depth, pending pods |
| Dropped | Packets dropped | Packet drop %, errors |
| Outstanding | Requested replicas or objects not yet running | Desired minus ready, `Pending` pods |
| Latency | Time to get a response | Pod start latency, PLEG, etcd fsync, API latency |
| Pressure | Node-level scarcity | `MemoryPressure`, `DiskPressure`, `PIDPressure`, PSI |

## Supervisor (object type 1)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| CPU Utilization above threshold | % | Derived | `cpu_used ÷ cpu_capacity` | see formulas | Sustained high use means more demand than capacity |
| Memory Utilization above threshold | % | Derived | `memory_used ÷ memory_capacity` | see formulas | |
| Storage Utilization above threshold | % | Derived | `storage_used ÷ storage_capacity` | see formulas | Capacity view: see consumption |
| Supervisor Services in Error | count | Derived | `config_status` = `ERROR` | count | A failed service blocks its functions (for example, a missing monitoring service) |
| Zone resource utilization | % | VC | `ZoneResourceUtilization` | not in the model | Returned 403 in the lab |

## Supervisor Namespace (object type 2)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| Storage quota exhausted | % of limit | SUP | `StoragePolicyQuota` `status.total[].scQuotaUsage.used` ÷ `status.appliedLimit` | see formulas | At 100 % new PVCs and VMs cannot be created in that policy |
| Storage reserved | bytes | SUP | `scQuotaUsage.reserved` | read as is | Reserved counts against quota before use |
| Namespace CPU / memory limit reached | % | VC | `resource_spec` | not verified | Not set in the lab (see [metrics.md](metrics.md)) |

## K8s Cluster (object type 4)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| Requests overcommit (CPU) | cores | Derived | Σ requests ÷ Σ allocatable | kubernetes-mixin `KubeCPUOvercommit`, `for` 10 min | Scheduler contention, not usage. Fires when requests exceed what the cluster can place if the largest node is lost (HA) |
| Requests overcommit (memory) | bytes | Derived | same for memory | `KubeMemoryOvercommit`, `for` 10 min | |
| Quota overcommit | ratio | K8S | Σ hard quotas ÷ allocatable | `KubeCPUQuotaOvercommit`, `> 1.5`, `for` 5 min | `namespaceOvercommitFactor` default 1.5 |
| Pods Pending (unscheduled) | count | K8S | `Pod` `status.phase` = `Pending` | count | Outstanding work. Often caused by insufficient CPU or memory |
| Pods not running | count | Derived | pods not in `Running` | count | Shown as "Number of Pods not Running" in VCF Operations |
| Node(s) Down | count | Derived | `Node` Ready = false | count | VCF Operations computed metric |
| Kubelet(s) Down | count | PROM | `up` for the kubelet job | count | `KubeletDown`, `for` 15 min |
| API server request error rate | % | PROM | `apiserver_request_total` with 5xx | 5xx ÷ total | `KubeClientErrors` above 1 % |
| Controller work queue depth | count | VCFO | "Controller Manager Work Queue Depth" | not published | VCF Operations metric. Upstream: `workqueue_depth` |
| IaaS controller workqueue depth | % | VCFO | "<Controller_Name> Workqueue Depth" | not published | Same idea, for the Supervisor controllers |

## K8s Node Pool (object type 5)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| Machines not ready | count | SUP | `spec.replicas − status.readyReplicas` | derived | A node is provisioned but not ready. Blocks rollouts |
| Rollout in progress | flag | SUP | `conditions[type=RollingOut]` | status | Scaling or upgrade pressure |

## K8s Node (object type 6)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| CPU Throttled (node-level) | — | — | none | — | Node has no CFS throttling. Use pods and containers |
| CPU PSI `some` avg10 | % | KS | `node.cpu.psi.some.avg10` | see formulas | At least one task waiting for CPU. VKS 1.35 only |
| CPU PSI `full` avg10 | % | KS | `node.cpu.psi.full.avg10` | see formulas | All non-idle tasks waiting. VKS 1.35 only |
| CPU PSI stall time | µs | KS | `node.cpu.psi.some.total` | rate of the counter | Use `Δ total ÷ Δ t` |
| Memory PSI `some` / `full` | % | KS | `node.memory.psi.*.avg10` | see formulas | VKS 1.35 only |
| I/O PSI `some` / `full` | % | KS | `node.io.psi.*.avg10` | see formulas | VKS 1.35 only |
| Memory pressure | flag | K8S | `conditions[type=MemoryPressure]` | status | `KubeNodePressure` (info, 10 min) |
| Disk pressure | flag | K8S | `conditions[type=DiskPressure]` | status | Same rule |
| PID pressure | flag | K8S | `conditions[type=PIDPressure]` | status | Same rule |
| Memory eviction signal | bytes | KS | `status.capacity.memory − node.memory.workingSetBytes` | derived | Eviction starts when this falls below the threshold (default `memory.available<100Mi` on Linux, verified in 1.37 docs) |
| Filesystem eviction signal | % | KS | `node.fs.availableBytes ÷ capacityBytes` | derived | `nodefs.available` |
| Inode eviction signal | % | KS | `node.fs.inodesFree ÷ inodes` | derived | `nodefs.inodesFree` |
| PID eviction signal | count | KS | `node.rlimit.maxpid − curproc` | derived | `pid.available` |
| Evictions | count / s | PROM | `kubelet_evictions` (label: eviction signal) | `rate(kubelet_evictions[15m])` | `KubeNodeEviction`, `for` 0 s. Kubelet metric, not in the lab |
| Network receive errors | errors/s | KS | `node.network.rxErrors` | `Δ ÷ Δ t` | Non-zero is contention or fault |
| Network transmit errors | errors/s | KS | `node.network.txErrors` | `Δ ÷ Δ t` | |
| Major page-fault rate | faults/s | KS | `node.memory.majorPageFaults` | `Δ ÷ Δ t` | Memory is being read from disk |
| Swap in use | bytes | KS | `node.swap.swapUsageBytes` | read as is | Swap use signals memory pressure. Not on ESX host nodes |
| Node readiness flapping | count | K8S | `Ready` condition changes | `changes(...[15m]) > 2` | `KubeNodeReadinessFlapping` |
| Pod start latency | seconds | PROM | `kubelet_pod_start_duration_seconds` | histogram | Not in the lab |
| PLEG relist duration | seconds | PROM | `kubelet_pleg_relist_duration_seconds` | p99 | `KubeletPlegDurationHigh` at 10 s |
| Packets dropped | % | VCFO | "Receive / Transmit Packets Dropped" | not published | VCF Operations metric. Not in the KS fields |
| Pods per node vs capacity | % | PROM | pods ÷ `status.capacity.pods` | `KubeletTooManyPods` at 0.95 | Scheduling contention |

## K8s Namespace (object type 7)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| Quota exhausted | ratio | K8S | `status.used ÷ status.hard` | `KubeQuotaAlmostFull` > 0.9; `KubeQuotaFullyUsed` = 1; `KubeQuotaExceeded` > 1 | `ResourceQuota`. Not in the lab (*(schema)*) |
| CPU throttling (top 95 %) | % | VCFO | "Top 95% CPU Throttling Workload's" | not published | Worst-case child. The 95th percentile ignores the top 5 % of samples |
| Out of memory events (top 95 %) | count | VCFO | "Top 95% Out Of Memory Events" | not published | |
| Pods not running | count | VCFO | "Number of Pods Not running" | count | |
| Network drop / error (top 95 %) | % | VCFO | "Top 95% Network Receive/Transmit Packets Drop", "... Errors Total" | not published | |

## K8s Workload (object type 8)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| Replicas not available | count | K8S | `spec.replicas − status.availableReplicas` | derived | Pods waiting to start |
| Replicas mismatch | count | K8S | `kube_deployment_spec_replicas > kube_deployment_status_replicas_available` | `KubeDeploymentReplicasMismatch`, `for` 15 min | PROM (kube-state-metrics) |
| StatefulSet mismatch | count | PROM | `kube_statefulset_status_replicas_ready != kube_statefulset_replicas` | `KubeStatefulSetReplicasMismatch`, `for` 15 min | |
| DaemonSet rollout stuck | count | PROM | `current_number_scheduled`, `number_misscheduled`, `number_available` vs desired | `KubeDaemonSetRolloutStuck`, `for` 15 min | |
| Collision count | count | K8S | `status.collisionCount` | count | Incremented when the controller's name hash collides with an existing revision. Not a failure count by itself. *(schema)* |
| CPU throttling (top 95 %) | % | VCFO | "Top 95% CPU Throttling Workload's" | not published | Deployment-level view |
| Out of memory events (top 95 %) | count | VCFO | "Top 95% Out Of Memory Events" | not published | |
| Pods not running | count | VCFO | "Pods Not Running" | count | |
| Outstanding (desired − ready) | count | K8S | `spec.replicas − status.readyReplicas` | derived | |

## K8s Pod (object type 9)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| CPU throttled ratio (worst container) | % | VCFO | "Worst Throttled Container" | not published | Upstream: `Δ cfs_throttled_periods ÷ Δ cfs_periods`. See [research-notes.md](research-notes.md) |
| CPU throttled periods ratio | % | PROM | `container_cpu_cfs_throttled_periods_total ÷ container_cpu_cfs_periods_total` | `CPUThrottlingHigh` > 25 % for 15 min | kubernetes-mixin default. Info-level alert |
| CPU throttled time | seconds / s | PROM | `container_cpu_cfs_throttled_seconds_total` | `Δ ÷ Δ t` | Time spent throttled |
| CPU PSI `some` / `full` (pod) | % | KS | `pods[].cpu.psi.some.avg10` | see formulas | VKS 1.35 only |
| Memory PSI `some` / `full` (pod) | % | KS | `pods[].memory.psi.*.avg10` | see formulas | VKS 1.35 only |
| Out of memory events | count | VCFO | "Total Out Of Memory Events" | not published | Upstream: `container_oom_events_total` (PROM). Not in the lab |
| Network receive / transmit packets dropped | % | VCFO | "Receive / Transmit Packets Dropped" | not published | |
| Network errors total | % | VCFO | "Receive / Transmit Errors Total" | not published | KS equivalent: `pods[].network.rxErrors` |
| Pod Pending | count | K8S | `status.phase` = `Pending` | count | Outstanding |
| Pod Pending for scheduling | — | K8S | `conditions[type=PodScheduled]` = `False` | status | Reason in the condition. Look for `Unschedulable` |
| Pod ContainersReady false | — | K8S | `conditions[type=ContainersReady]` | status | Startup contention, for example image pull |
| Volume usage | % | KS | `pods[].volume[].usedBytes ÷ capacityBytes` | derived | Storage contention on a PVC. See consumption |

## K8s Container (object type 10)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| CPU throttled (container) | % | VCFO | "Throttled" | not published | Container CPU metric in VCF Operations |
| CPU throttled periods ratio | % | PROM | `container_cpu_cfs_throttled_periods_total ÷ container_cpu_cfs_periods_total` | rate over 5 min | Same as pod level, per container |
| CPU throttled time | s/s | PROM | `container_cpu_cfs_throttled_seconds_total` | rate | |
| CPU PSI `some` / `full` | % | KS | `containers[].cpu.psi.some.avg10` | see formulas | VKS 1.35 only |
| Memory PSI `some` / `full` | % | KS | `containers[].memory.psi.*` | see formulas | VKS 1.35 only |
| Memory limit reached | % | Derived | `workingSetBytes ÷ limits.memory` | derived | Near 100 % means OOM is close. Limits are enforced reactively |
| OOM killed | flag | K8S | `status.containerStatuses[].lastState.terminated.reason` = `OOMKilled` | status | Exit code 137 |
| Out of memory events | count | PROM | `container_oom_events_total` | `increase()` | Not in the lab |
| CrashLoopBackOff | flag | K8S | `state.waiting.reason` = `CrashLoopBackOff` | status | Latency and restart contention. See availability |
| Restart count | count | K8S | `status.containerStatuses[].restartCount` | count | |
| Image pull back-off | flag | K8S | `state.waiting.reason` = `ImagePullBackOff` | status | Registry contention |

## Events that show contention

These come from the Event API (`EVT`). Events have a limited retention and are best-effort (Kubernetes docs), so use them to confirm a cause, not to count it over time.

| Event reason | Type | Object | What it means | Verified |
|---|---|---|---|---|
| `FailedScheduling` | Warning | Pod | No node fits (CPU, memory, taints, affinity) | Source: kube-scheduler (third-party guide) |
| `Preempting` | Normal | Pod | A higher priority pod evicts this one | Upstream scheduler (not verified in the lab) |
| `Evicted` | Warning | Pod | Kubelet evicted the pod under node pressure | Yes: kubelet 1.35.9 source (reason `Evicted`) |
| `EvictionThresholdMet` | Warning | Node | Eviction threshold crossed, kubelet reclaims | Yes: kubelet 1.35.9 source |
| OOM kill | — | Container | `OOMKilled` in container status, not an event | Yes: kubelet docs. No OOM event in kubelet 1.35.9 source |
| `FailedMount` | Warning | Pod | Volume could not be mounted (storage contention) | Kubelet constant `FailedMountVolume` = `FailedMount` (source search) |
| `BackOff` | Warning | Container | Crash loop back-off | Kubelet `BackOff` (source search) |
| `Unhealthy` | Warning | Pod | Probe failed | Kubelet `ContainerUnhealthy` = `Unhealthy` (source search) |
