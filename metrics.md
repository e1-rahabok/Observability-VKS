# VKS Object Metrics

Metrics (numeric attributes) for each object type in the VKS object model, taken from the live APIs of a VCF 9.1 lab: vCenter REST API, Supervisor Kubernetes API v1.32, and VKS cluster Kubernetes API v1.35 (VKS 3.6, ClusterClass `builtin-generic-v3.6.0`, Cluster API `v1beta2`). Each metric names the API field it comes from, so it can be checked against the manual.

Non-numeric attributes (status, conditions, versions, names) are properties and are listed in [properties.md](properties.md). The raw field-name lists these metrics were selected from are in [raw/](raw/).

**Source legend**

| Code | API |
|---|---|
| VC | vCenter REST API: `/api/vcenter/namespace-management/*`, `/api/vcenter/namespaces/*` |
| SUP | Supervisor Kubernetes API (port 6443). Login: `POST https://<supervisor>/wcp/login` with vCenter SSO credentials |
| K8S | Kubernetes API of the cluster the object lives in (VKS cluster, or the Supervisor for Supervisor-side objects). VKS kubeconfig: Supervisor secret `<namespace>/<cluster>-kubeconfig` |
| KS | Kubelet Summary API: `/api/v1/nodes/<node>/proxy/stats/summary`, through the K8S or SUP API |
| MS | Metrics API `metrics.k8s.io/v1beta1` (metrics-server). VKS clusters only: the Supervisor returns 403 for `administrator@vsphere.local` |
| Derived | Counted, summed or computed from other fields |

Conventions:

- KS fields are written relative to the summary entry: `node.*` for a node, `pods[].*` for a pod, `containers[].*` for a container (`pods[].containers[]`).
- KS CPU comes in two forms: `usageNanoCores` (current rate) and `usageCoreNanoSeconds` (cumulative counter). MS reports the rate as a quantity string (for example `106654804n` for CPU, `2000240Ki` for memory).
- **PSI** (Pressure Stall Information) is `{cpu,memory,io}.psi.{some,full}.{avg10,avg60,avg300,total}`. It appears on VKS clusters (Kubernetes 1.35) but not on the Supervisor (Kubernetes 1.32).
- *(schema)* means the field is part of the Kubernetes API schema but was zero or absent in the lab. Kubernetes omits a status field whose value is zero, so these were not seen live.
- "Not on ESX host nodes" and "Not on vSphere Pods" mark gaps in Supervisor coverage. See [Notes](#notes-for-validating-the-manual).

| Object Type | Metric | Unit | Source | API field | Notes |
|---|---|---|---|---|---|
| Supervisor | CPU Capacity | MHz | VC | `supervisors/summaries` → `info.stats.cpu_capacity` | |
| Supervisor | CPU Used | MHz | VC | `info.stats.cpu_used` | |
| Supervisor | Memory Capacity | MB | VC | `info.stats.memory_capacity` | |
| Supervisor | Memory Used | MB | VC | `info.stats.memory_used` | |
| Supervisor | Storage Capacity | MB | VC | `info.stats.storage_capacity` | |
| Supervisor | Storage Used | MB | VC | `info.stats.storage_used` | |
| Supervisor | CPU / Memory / Storage Utilization | % | Derived | used ÷ capacity | |
| Supervisor | Number of Supervisor Namespaces | count | Derived | VC `/api/vcenter/namespaces/instances` | |
| Supervisor | Number of VKS Clusters | count | Derived | SUP `cluster.x-k8s.io` `Cluster` | |
| Supervisor | Number of Control Plane Nodes | count | Derived | SUP Nodes with `labels[node-role.kubernetes.io/control-plane]` | |
| Supervisor | Number of ESX Host Nodes | count | Derived | SUP Nodes with `labels[node-role.kubernetes.io/agent]` | Spherelet nodes |
| Supervisor | Number of vSphere Pods | count | Derived | SUP Pods in user namespaces | |
| Supervisor | Number of Supervisor Services | count | Derived | VC `supervisors/{id}/supervisor-services` | |
| Supervisor | Number of Supervisor Services in Error | count | Derived | VC `config_status` = `ERROR` | |
| Supervisor Namespace | CPU Used | MHz | VC | `namespaces/instances/v2/{ns}` → `stats.cpu_used` | |
| Supervisor Namespace | Memory Used | MB | VC | `stats.memory_used` | |
| Supervisor Namespace | Storage Used | MB | VC | `stats.storage_used` | |
| Supervisor Namespace | CPU / Memory Limit | | VC | `resource_spec` | Not set in the lab; field names not verified |
| Supervisor Namespace | Storage Limit (per storage policy) | bytes | SUP | `StoragePolicyQuota` `spec.limit`, `status.appliedLimit` | |
| Supervisor Namespace | Storage Used (per storage class) | bytes | SUP | `StoragePolicyQuota` `status.total[].scQuotaUsage.used` | |
| Supervisor Namespace | Storage Reserved (per storage class) | bytes | SUP | `StoragePolicyQuota` `status.total[].scQuotaUsage.reserved` | |
| Supervisor Namespace | Storage Used / Reserved (per extension) | bytes | SUP | `StoragePolicyQuota` `status.extensions[].extensionQuotaUsage[].scQuotaUsage.used`, `.reserved` | Extension: VM, PVC, snapshot … |
| Supervisor Namespace | Number of VKS Clusters | count | Derived | SUP `Cluster` in namespace | |
| Supervisor Namespace | Number of VMs (VM Service) | count | Derived | SUP `vmoperator.vmware.com` `VirtualMachine` in namespace | |
| Supervisor Namespace | Number of vSphere Pods | count | Derived | SUP Pods in namespace | |
| K8s Cluster | Control Plane Nodes Desired | count | SUP | `Cluster` `status.controlPlane.desiredReplicas` | |
| K8s Cluster | Control Plane Nodes | count | SUP | `status.controlPlane.replicas` | |
| K8s Cluster | Control Plane Nodes Ready | count | SUP | `status.controlPlane.readyReplicas` | |
| K8s Cluster | Control Plane Nodes Available | count | SUP | `status.controlPlane.availableReplicas` | |
| K8s Cluster | Control Plane Nodes Up-to-date | count | SUP | `status.controlPlane.upToDateReplicas` | |
| K8s Cluster | Worker Nodes Desired | count | SUP | `Cluster` `status.workers.desiredReplicas` | |
| K8s Cluster | Worker Nodes | count | SUP | `status.workers.replicas` | |
| K8s Cluster | Worker Nodes Ready | count | SUP | `status.workers.readyReplicas` | |
| K8s Cluster | Worker Nodes Available | count | SUP | `status.workers.availableReplicas` | |
| K8s Cluster | Worker Nodes Up-to-date | count | SUP | `status.workers.upToDateReplicas` | |
| K8s Cluster | Number of Node Pools | count | Derived | SUP `MachineDeployment` per cluster | |
| K8s Cluster | Number of Namespaces | count | Derived | K8S `Namespace` | |
| K8s Cluster | Number of Workloads (by type) | count | Derived | K8S `apps/v1`, `batch/v1` kinds | |
| K8s Cluster | Number of Pods (by phase) | count | Derived | K8S `Pod` `status.phase` | |
| K8s Cluster | Number of Containers | count | Derived | K8S `Pod` `spec.containers[]` | |
| K8s Cluster | CPU Capacity / Allocatable | cores | Derived | Σ Node `status.capacity.cpu`, `status.allocatable.cpu` | |
| K8s Cluster | Memory Capacity / Allocatable | bytes | Derived | Σ Node `status.capacity.memory`, `status.allocatable.memory` | |
| K8s Cluster | Pod Capacity | count | Derived | Σ Node `status.allocatable.pods` | |
| K8s Cluster | CPU Usage | cores | Derived | Σ Node CPU usage (MS or KS) | |
| K8s Cluster | Memory Usage (working set) | bytes | Derived | Σ Node memory working set (MS or KS) | |
| K8s Cluster | CPU / Memory Requests, Limits | cores / bytes | Derived | Σ container `resources.requests`, `resources.limits` | |
| K8s Node Pool | Desired Nodes | count | SUP | `Cluster` `spec.topology.workers.machineDeployments[].replicas` | |
| K8s Node Pool | Nodes | count | SUP | `MachineDeployment` `status.replicas` | |
| K8s Node Pool | Nodes Ready | count | SUP | `status.readyReplicas` | |
| K8s Node Pool | Nodes Available | count | SUP | `status.availableReplicas` | |
| K8s Node Pool | Nodes Up-to-date | count | SUP | `status.upToDateReplicas` | |
| K8s Node | CPU Capacity / Allocatable | cores | K8S | `Node` `status.capacity.cpu`, `status.allocatable.cpu` | |
| K8s Node | Memory Capacity / Allocatable | bytes | K8S | `status.capacity.memory`, `status.allocatable.memory` | |
| K8s Node | Pod Capacity / Allocatable | count | K8S | `status.capacity.pods`, `status.allocatable.pods` | |
| K8s Node | Ephemeral Storage Capacity / Allocatable | bytes | K8S | `status.capacity.ephemeral-storage`, `status.allocatable.ephemeral-storage` | Not on ESX host nodes |
| K8s Node | Hugepages 2Mi / 1Gi Capacity | bytes | K8S | `status.capacity.hugepages-2Mi`, `hugepages-1Gi` | Not on ESX host nodes |
| K8s Node | CPU Usage | nanocores | KS | `node.cpu.usageNanoCores` | Not on ESX host nodes |
| K8s Node | CPU Usage (cumulative) | ns | KS | `node.cpu.usageCoreNanoSeconds` | Not on ESX host nodes |
| K8s Node | CPU Usage | cores | MS | `NodeMetrics` `usage.cpu` | VKS only |
| K8s Node | Memory Usage | bytes | KS | `node.memory.usageBytes` | Not on ESX host nodes |
| K8s Node | Memory Working Set | bytes | KS / MS | `node.memory.workingSetBytes`; `NodeMetrics` `usage.memory` | Not on ESX host nodes; MS VKS only |
| K8s Node | Memory RSS | bytes | KS | `node.memory.rssBytes` | Not on ESX host nodes |
| K8s Node | Memory Available | bytes | KS | `node.memory.availableBytes` | Not on ESX host nodes |
| K8s Node | Memory Page Faults / Major Page Faults | count | KS | `node.memory.pageFaults`, `.majorPageFaults` | Not on ESX host nodes |
| K8s Node | Swap Usage / Available | bytes | KS | `node.swap.swapUsageBytes`, `.swapAvailableBytes` | Not on ESX host nodes |
| K8s Node | Network Received / Transmitted | bytes | KS | `node.network.rxBytes`, `.txBytes` (also per `interfaces[]`) | Not on ESX host nodes |
| K8s Node | Network Receive / Transmit Errors | count | KS | `node.network.rxErrors`, `.txErrors` | Not on ESX host nodes |
| K8s Node | Filesystem Capacity / Used / Available | bytes | KS | `node.fs.capacityBytes`, `.usedBytes`, `.availableBytes` | Not on ESX host nodes |
| K8s Node | Filesystem Inodes / Used / Free | count | KS | `node.fs.inodes`, `.inodesUsed`, `.inodesFree` | Not on ESX host nodes |
| K8s Node | Image FS Capacity / Used / Available (+ inodes) | bytes | KS | `node.runtime.imageFs.*` | Not on ESX host nodes |
| K8s Node | Container FS Capacity / Used / Available (+ inodes) | bytes | KS | `node.runtime.containerFs.*` | Not on ESX host nodes |
| K8s Node | Processes Running / Max PIDs | count | KS | `node.rlimit.curproc`, `.maxpid` | Not on ESX host nodes |
| K8s Node | CPU / Memory / IO Pressure (PSI) | % / µs | KS | `node.{cpu,memory,io}.psi.*` | VKS only |
| K8s Node | System Container CPU / Memory | nanocores / bytes | KS | `node.systemContainers[].cpu.*`, `.memory.*` | kubelet, runtime, pods. Not on ESX host nodes |
| K8s Node | Number of Pods | count | Derived | Pods with `spec.nodeName` = node | |
| K8s Node | CPU / Memory Requests, Limits | cores / bytes | Derived | Σ container `resources` of pods on the node | |
| K8s Namespace | Number of Pods / Containers / Workloads | count | Derived | K8S objects in the namespace | |
| K8s Namespace | CPU Usage | cores | Derived | Σ pod CPU (MS or KS) | |
| K8s Namespace | Memory Usage (working set) | bytes | Derived | Σ pod memory (MS or KS) | |
| K8s Namespace | CPU / Memory Requests, Limits | cores / bytes | Derived | Σ container `resources` | |
| K8s Namespace | Quota Hard (per resource) | per resource | K8S | `ResourceQuota` `status.hard.<resource>` | *(schema)* |
| K8s Namespace | Quota Used (per resource) | per resource | K8S | `ResourceQuota` `status.used.<resource>` | *(schema)* |
| K8s Workload | Desired | count | K8S | Deployment, StatefulSet, ReplicaSet `spec.replicas`; DaemonSet `status.desiredNumberScheduled`; Job `spec.completions` | Not CronJob |
| K8s Workload | Current | count | K8S | Deployment, ReplicaSet `status.replicas`; StatefulSet `status.replicas`, `status.currentReplicas`; DaemonSet `status.currentNumberScheduled`; Job `status.active` *(schema)*; CronJob count of `status.active[]` *(schema)* | |
| K8s Workload | Ready | count | K8S | Deployment, StatefulSet, ReplicaSet `status.readyReplicas`; DaemonSet `status.numberReady`; Job `status.ready` | Not CronJob |
| K8s Workload | Available | count | K8S | Deployment, StatefulSet, ReplicaSet `status.availableReplicas`; DaemonSet `status.numberAvailable` | |
| K8s Workload | Unavailable | count | K8S | Deployment `status.unavailableReplicas` *(schema)*; DaemonSet `status.numberUnavailable` *(schema)* | |
| K8s Workload | Updated | count | K8S | Deployment, StatefulSet `status.updatedReplicas`; DaemonSet `status.updatedNumberScheduled` | |
| K8s Workload | Terminating | count | K8S | Deployment, ReplicaSet `status.terminatingReplicas`; Job `status.terminating` | |
| K8s Workload | Misscheduled | count | K8S | DaemonSet `status.numberMisscheduled` | |
| K8s Workload | Fully Labeled | count | K8S | ReplicaSet `status.fullyLabeledReplicas` | |
| K8s Workload | Succeeded / Failed | count | K8S | Job `status.succeeded`, `status.failed` *(schema)* | |
| K8s Workload | Collision Count | count | K8S | StatefulSet `status.collisionCount`; Deployment, DaemonSet `status.collisionCount` *(schema)* | |
| K8s Workload | Number of Pods | count | Derived | Pods owned by the workload | All workload types |
| K8s Workload | CPU / Memory Usage | cores / bytes | Derived | Σ pod usage (MS or KS) | All workload types |
| K8s Workload | CPU / Memory Requests, Limits | cores / bytes | Derived | Σ container `resources` of its pods | All workload types |
| K8s Pod | CPU Usage | nanocores | KS | `pods[].cpu.usageNanoCores` | Not on vSphere Pods |
| K8s Pod | CPU Usage (cumulative) | ns | KS | `pods[].cpu.usageCoreNanoSeconds` | |
| K8s Pod | CPU Usage | cores | MS | `PodMetrics` Σ `containers[].usage.cpu` | VKS only |
| K8s Pod | Memory Usage | bytes | KS | `pods[].memory.usageBytes` | |
| K8s Pod | Memory Working Set / RSS / Available | bytes | KS | `pods[].memory.workingSetBytes`, `.rssBytes`, `.availableBytes` | Not on vSphere Pods |
| K8s Pod | Memory Page Faults / Major Page Faults | count | KS | `pods[].memory.pageFaults`, `.majorPageFaults` | Not on vSphere Pods |
| K8s Pod | Swap Usage | bytes | KS | `pods[].swap.swapUsageBytes` | Not on vSphere Pods |
| K8s Pod | Network Received / Transmitted | bytes | KS | `pods[].network.rxBytes`, `.txBytes` (+ `interfaces[]`) | vSphere Pods: per interface only |
| K8s Pod | Network Receive / Transmit Errors | count | KS | `pods[].network.rxErrors`, `.txErrors` | vSphere Pods: per interface only |
| K8s Pod | Ephemeral Storage Capacity / Used / Available (+ inodes) | bytes | KS | `pods[].ephemeral-storage.*` | Not on vSphere Pods |
| K8s Pod | Volume Capacity / Used / Available (+ inodes), per volume | bytes | KS | `pods[].volume[].capacityBytes`, `.usedBytes`, `.availableBytes`, `.inodes*` | Includes PVCs |
| K8s Pod | Number of Processes | count | KS | `pods[].process_stats.process_count` | Not on vSphere Pods |
| K8s Pod | CPU / Memory / IO Pressure (PSI) | % / µs | KS | `pods[].{cpu,memory,io}.psi.*` | VKS only |
| K8s Pod | Number of Containers | count | Derived | `spec.containers[]` | |
| K8s Pod | Container Restarts (total) | count | Derived | Σ `status.containerStatuses[].restartCount` | |
| K8s Pod | CPU / Memory Requests, Limits | cores / bytes | Derived | Σ `spec.containers[].resources.requests`, `.limits` | |
| K8s Container | CPU Usage | nanocores | KS | `containers[].cpu.usageNanoCores` | |
| K8s Container | CPU Usage (cumulative) | ns | KS | `containers[].cpu.usageCoreNanoSeconds` | |
| K8s Container | CPU Usage | cores | MS | `PodMetrics` `containers[].usage.cpu` | VKS only |
| K8s Container | Memory Usage | bytes | KS | `containers[].memory.usageBytes` | |
| K8s Container | Memory Working Set | bytes | KS / MS | `containers[].memory.workingSetBytes`; `PodMetrics` `containers[].usage.memory` | MS VKS only |
| K8s Container | Memory RSS / Available | bytes | KS | `containers[].memory.rssBytes`, `.availableBytes` | |
| K8s Container | Memory Page Faults / Major Page Faults | count | KS | `containers[].memory.pageFaults`, `.majorPageFaults` | |
| K8s Container | Swap Usage / Available | bytes | KS | `containers[].swap.swapUsageBytes`, `.swapAvailableBytes` | Not on vSphere Pods |
| K8s Container | Root FS Capacity / Used / Available (+ inodes) | bytes | KS | `containers[].rootfs.*` | vSphere Pods: Used and inodesUsed only |
| K8s Container | Log FS Capacity / Used / Available (+ inodes) | bytes | KS | `containers[].logs.*` | vSphere Pods: Used and inodesUsed only |
| K8s Container | CPU / Memory / IO Pressure (PSI) | % / µs | KS | `containers[].{cpu,memory,io}.psi.*` | VKS only |
| K8s Container | Restart Count | count | K8S | `Pod` `status.containerStatuses[].restartCount` | |
| K8s Container | Last Exit Code | code | K8S | `status.containerStatuses[].lastState.terminated.exitCode` | |
| K8s Container | CPU Request / Limit | cores | K8S | `spec.containers[].resources.requests.cpu`, `.limits.cpu` | |
| K8s Container | Memory Request / Limit | bytes | K8S | `spec.containers[].resources.requests.memory`, `.limits.memory` | |

Supervisor Service has no metrics; see its properties in [properties.md](properties.md).

## Notes for validating the manual

- **Supervisor ESX host nodes have no usage metrics.** The Supervisor's nodes include the ESX hosts (spherelet nodes). The Kubelet Summary API returns no node-level stats for them, and `Node` capacity has only `cpu`, `memory` and `pods`.
- **vSphere Pods expose fewer metrics than VKS pods.** At pod level there is only the cumulative CPU counter (no current rate), memory usage, network per interface and volume stats. Working set, ephemeral storage and process count are missing.
- **The Supervisor blocks its Metrics API.** `metrics.k8s.io` returns 403 for `administrator@vsphere.local`. The Kubelet Summary API through the Supervisor API works.
- **PSI pressure metrics** exist only on VKS clusters (Kubernetes 1.35), not on the Supervisor (1.32).
- **VKS clusters are Cluster API `Cluster` objects** (`cluster.x-k8s.io/v1beta2`). `TanzuKubernetesCluster` is legacy and had no instances. Node counts use the `v1beta2` field names (`desiredReplicas`, `readyReplicas`, `availableReplicas`, `upToDateReplicas`).
- **Containers are not API objects.** They are entries inside a Pod (`spec.containers[]`, `status.containerStatuses[]`) and inside a KS `pods[].containers[]` entry.
- **Not modelled as separate object types.** These are folded into the object types above: `ResourceQuota` (K8s Namespace), `StoragePolicyQuota` (Supervisor Namespace), `KubeadmControlPlane` (K8s Cluster), `Machine` and `VirtualMachine` (1:1 with K8s Node), `PersistentVolumeClaim` (pod `volume[]` stats).

## Gaps in the evidence

- **Fields marked *(schema)*** were zero or absent in the lab, so their names come from the Kubernetes API definition, not from live data.
- **Supervisor Namespace CPU and memory limits** (`resource_spec`) were not set on any lab namespace, so those field names are not verified.
- **Zone utilization** (`topology.tanzu.vmware.com` `ZoneResourceUtilization`) returned 403, so it is not in the model.
