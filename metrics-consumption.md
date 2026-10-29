# VKS Consumption Metrics

Consumption metrics show how much of a resource is used: CPU utilization and run time, memory used, network throughput, and disk I/O. Disk **space** (bytes used or free on a filesystem, volume or quota) is capacity, not consumption; it is in the [Capacity](#capacity-disk-space) section at the end.

Grouped by object type, in the same order as [README.md](README.md). Formulas are in [metrics-formulas.md](metrics-formulas.md). Contention (waiting or refused work) is in [metrics-contention.md](metrics-contention.md).

Source codes are those of [metrics.md](metrics.md), plus `PROM` and `VCFO` (see [metrics-formulas.md](metrics-formulas.md#source-codes)).

## Consumption types

| Type | Examples | Unit |
|---|---|---|
| Utilization | CPU %, memory % of limit or allocatable | % |
| Run / used | CPU cores in use, CPU-seconds (cumulative) | cores, ns |
| Memory used | working set, RSS | bytes |
| Throughput | network bytes/s, packets/s | bytes/s |
| I/O | disk reads/writes per second, bytes per second | IOPS, bytes/s (not in the lab model) |

The lab model has no disk I/O fields (IOPS or bytes per second for block devices). cAdvisor exposes filesystem read and write counters per container, but they were not collected in the lab and are not included here.

## Supervisor (object type 1)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| CPU Used | MHz | VC | `info.stats.cpu_used` | read as is | Hypervisor view. Not comparable to Kubernetes cores |
| CPU Utilization | % | Derived | `cpu_used ÷ cpu_capacity` | see formulas | |
| Memory Used | MB | VC | `info.stats.memory_used` | read as is | |
| Memory Utilization | % | Derived | `memory_used ÷ memory_capacity` | see formulas | |
| Number of VKS Clusters | count | Derived | `Cluster` objects | count | |

## Supervisor Namespace (object type 2)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| CPU Used | MHz | VC | `namespaces/instances/v2/{ns}` → `stats.cpu_used` | read as is | |
| Memory Used | MB | VC | `stats.memory_used` | read as is | |
| Number of VMs | count | Derived | `VirtualMachine` objects in the namespace | count | VM Service |
| Number of vSphere Pods | count | Derived | pods in the namespace on ESX host nodes | count | |

## K8s Cluster (object type 4)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| CPU Usage | cores | Derived | Σ over nodes of `node.cpu.usageNanoCores ÷ 1e9` | sum | KS, or MS on VKS |
| CPU Usage (VCF Operations) | cores | VCFO | "Usage (Cores)" | not published | |
| Memory Usage (working set) | bytes | Derived | Σ over nodes of `node.memory.workingSetBytes` | sum | |
| Memory Usage (VCF Operations) | MB | VCFO | "Usage (MB)" | not published | |
| Pods running | count | K8S | `Pod` `status.phase` = `Running` | count | |
| Containers | count | Derived | Σ `spec.containers[]` | count | |
| Total Usage (VKS) | GB | VCFO | "VKS Cluster: Total Usage" | not published | VKS summary |
| Usage % (VKS) | % | VCFO | "VKS Cluster: Usage" | not published | VKS summary |

## K8s Node Pool (object type 5)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| Nodes | count | SUP | `MachineDeployment` `status.replicas` | read as is | Node pool size. Not consumption, but it sets the capacity |

## K8s Node (object type 6)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| CPU Usage | nanocores | KS | `node.cpu.usageNanoCores` | read as is | Not on ESX host nodes |
| CPU Usage | cores | MS | `NodeMetrics` `usage.cpu` | `÷ 1e9` for nanocores | VKS only |
| CPU Utilization | % | Derived | `usageNanoCores ÷ (allocatable.cpu × 1e9)` | see formulas | |
| CPU Usage (cumulative) | ns | KS | `node.cpu.usageCoreNanoSeconds` | counter | Use `Δ ÷ Δ t` |
| CPU requests | cores | Derived | Σ container requests on the node | sum | Scheduler view |
| Memory Usage | bytes | KS | `node.memory.usageBytes` | read as is | Not on ESX host nodes |
| Memory Working Set | bytes | KS / MS | `node.memory.workingSetBytes`; `NodeMetrics` `usage.memory` | read as is | Used for the eviction signal |
| Memory Utilization | % | Derived | `workingSetBytes ÷ allocatable.memory` | see formulas | |
| Memory RSS | bytes | KS | `node.memory.rssBytes` | read as is | Anonymous memory, not cache |
| Network Received | bytes/s | Derived | `Δ node.network.rxBytes ÷ Δ t` | rate | Also per interface |
| Network Transmitted | bytes/s | Derived | `Δ node.network.txBytes ÷ Δ t` | rate | |
| Processes running | count | KS | `node.rlimit.curproc` | read as is | Share of `maxpid` |
| CPU / Memory / IO Use (PSI) | % | KS | PSI `some.avg10` | see formulas | Pressure, see contention |
| System container CPU / Memory | nanocores / bytes | KS | `node.systemContainers[].cpu.*`, `.memory.*` | read as is | kubelet, runtime and pods reserved. Not on ESX host nodes |
| Pods running on node | count | Derived | `Pod` with `spec.nodeName` | count | |
| Network throughput (VCF Operations) | % | VCFO | Network metrics | not published | Not in the KS model |

## K8s Namespace (object type 7)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| CPU Usage | cores | Derived | Σ over pods of `pods[].cpu.usageNanoCores ÷ 1e9` | sum | |
| Memory Usage | bytes | Derived | Σ over pods of `pods[].memory.workingSetBytes` | sum | |
| CPU Usage (VCF Operations) | millicores | VCFO | "Usage (Millicores)" | not published | Namespace view |
| Memory Usage (VCF Operations) | MB | VCFO | "Usage (MB)" | not published | |
| Number of Deployments / StatefulSets / DaemonSets | count | VCFO | counts | count | |
| Number of Pods / Containers / Namespaces | count | VCFO | counts | count | |

## K8s Workload (object type 8)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| CPU Usage | cores | Derived | Σ pod usage | sum | |
| Memory Usage | bytes | Derived | Σ pod working set | sum | |
| Replicas | count | K8S | `spec.replicas` / `status.replicas` | read as is | Consumption of pod slots |
| Number of Pods | count | Derived | pods owned by the workload | count | |

## K8s Pod (object type 9)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| CPU Usage | nanocores | KS | `pods[].cpu.usageNanoCores` | read as is | Not on vSphere Pods |
| CPU Usage (cumulative) | ns | KS | `pods[].cpu.usageCoreNanoSeconds` | counter | |
| CPU Usage (MS) | cores | MS | Σ `containers[].usage.cpu` | sum | VKS only |
| CPU Usage (VCF Operations) | millicores | VCFO | "Usage (Millicores)" | not published | |
| CPU Requests / Limits | millicores | VCFO | "Requests", "Limits" (properties in VCF Operations) | read as is | Properties in VCF Operations, metrics here (see [metrics.md](metrics.md)) |
| Memory Usage | bytes | KS | `pods[].memory.usageBytes` | read as is | |
| Memory Working Set | bytes | KS | `pods[].memory.workingSetBytes` | read as is | |
| Memory RSS | bytes | KS | `pods[].memory.rssBytes` | read as is | Not on vSphere Pods |
| Memory Utilization | % | Derived | `workingSetBytes ÷ Σ limits.memory` | see formulas | Undefined when there is no limit |
| Network Received / Transmitted | bytes/s | Derived | `Δ pods[].network.rxBytes ÷ Δ t` | rate | vSphere Pods: per interface only |
| Number of Processes | count | KS | `pods[].process_stats.process_count` | read as is | Not on vSphere Pods |
| Memory Usage (VCF Operations) | MB | VCFO | "Usage (MB)" | not published | |

## K8s Container (object type 10)

| Metric | Unit | Source | Field or name | Formula | Notes |
|---|---|---|---|---|---|
| CPU Usage | nanocores | KS | `containers[].cpu.usageNanoCores` | read as is | |
| CPU Utilization | % | Derived | `usageNanoCores ÷ (limits.cpu × 1e9)` | see formulas | Against the limit (CFS enforces it) |
| CPU Run time | seconds | PROM | `container_cpu_usage_seconds_total` | `rate(...[5m])` | cAdvisor. Not in the lab. Equivalent to the cumulative KS counter |
| CPU Usage (VCF Operations) | millicores / % | VCFO | "Usage (Millicores)", "Usage (%)" | not published | |
| Memory Usage | bytes | KS | `containers[].memory.usageBytes` | read as is | |
| Memory Working Set | bytes | KS / MS | `containers[].memory.workingSetBytes`; `PodMetrics` `containers[].usage.memory` | read as is | |
| Memory Utilization | % | Derived | `workingSetBytes ÷ limits.memory` | see formulas | |
| Memory RSS | bytes | KS | `containers[].memory.rssBytes` | read as is | |
| Memory Usage (VCF Operations) | MB / % | VCFO | "Usage (MB)", "Usage (%)" | not published | |

## Consumption that VCF Operations shows but the lab did not collect

| Metric | Object | Unit | Source | Name in VCF Operations | Notes |
|---|---|---|---|---|---|
| Container Usage % | Container | % | VCFO | "Usage (Metric, %)" | Formula not published |
| Node CPU Usage | Node | millicores | VCFO | "CPU: Usage" | Unit as listed by VCF Operations |
| Node Total Used | Node | GB | VCFO | "Memory: Total Used" | |
| Etcd DB size in use | Control plane (node) | bytes | VCFO | "Mvcc DB Size In Use" | Control plane only. Upstream etcd name `etcd_mvcc_db_total_size_in_use_in_bytes` (PROM), not verified here |
| Etcd server used / size | Control plane (node) | bytes | VCFO | "Server Used", "Server Size" | |
| PVCs with utilization > 80 % | VKS cluster | count | VCFO | "Number of PVCs with utilization greater than 80" | Derived from volume usage (see capacity) |

## Capacity: disk space

Kept apart from consumption, as requested. Capacity answers "how much is free?" and "when does it run out?"

| Object Type | Metric | Unit | Source | API field | Formula | Notes |
|---|---|---|---|---|---|---|
| Supervisor | Storage Capacity | MB | VC | `info.stats.storage_capacity` | read as is | |
| Supervisor | Storage Used | MB | VC | `info.stats.storage_used` | read as is | |
| Supervisor | Storage Utilization | % | Derived | `storage_used ÷ storage_capacity` | see formulas | |
| Supervisor Namespace | Storage Used | MB | VC | `stats.storage_used` | read as is | |
| Supervisor Namespace | Storage Used (per storage class) | bytes | SUP | `StoragePolicyQuota` `status.total[].scQuotaUsage.used` | read as is | Quota view |
| Supervisor Namespace | Storage Reserved (per storage class) | bytes | SUP | `scQuotaUsage.reserved` | read as is | |
| Supervisor Namespace | Storage Limit (per policy) | bytes | SUP | `StoragePolicyQuota` `spec.limit`, `status.appliedLimit` | read as is | |
| K8s Namespace | Quota Hard / Used (storage) | bytes | K8S | `ResourceQuota` `status.hard`, `status.used` (`requests.storage`) | `used ÷ hard` | *(schema)*, not in the lab |
| K8s Namespace | PVC Storage Requested | bytes | K8S | Σ PVC `spec.resources.requests.storage` | sum | Vanilla only; not collected in the lab |
| K8s Node | Filesystem Capacity / Used / Available | bytes | KS | `node.fs.capacityBytes`, `.usedBytes`, `.availableBytes` | `usedBytes ÷ capacityBytes` | Not on ESX host nodes |
| K8s Node | Filesystem Inodes / Used / Free | count | KS | `node.fs.inodes`, `.inodesUsed`, `.inodesFree` | `inodesUsed ÷ inodes` | |
| K8s Node | Image FS Capacity / Used / Available | bytes | KS | `node.runtime.imageFs.*` | `usedBytes ÷ capacityBytes` | |
| K8s Node | Container FS Capacity / Used / Available | bytes | KS | `node.runtime.containerFs.*` | `usedBytes ÷ capacityBytes` | |
| K8s Pod | Ephemeral Storage Capacity / Used / Available | bytes | KS | `pods[].ephemeral-storage.*` | `usedBytes ÷ capacityBytes` | Not on vSphere Pods |
| K8s Pod | Volume Capacity / Used / Available (per volume) | bytes | KS | `pods[].volume[].capacityBytes`, `.usedBytes`, `.availableBytes` | `usedBytes ÷ capacityBytes` | Includes PVCs (`pvcRef`) |
| K8s Container | Root FS / Log FS Used | bytes | KS | `containers[].rootfs.usedBytes`, `containers[].logs.usedBytes` | read as is | vSphere Pods: used only |
| K8s Cluster | PVCs with utilization > 80 % | count | VCFO | "Number of PVCs with utilization greater than 80" | count | |
| Derived (kubelet alerts) | Volume filling up in 4 days | — | PROM | `kubelet_volume_stats_*` | linear prediction | kubernetes-mixin `KubePersistentVolumeFillingUp`: warning below 15 % free, critical below 3 % free |
