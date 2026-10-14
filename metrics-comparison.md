# VKS vs Vanilla Kubernetes: Metrics Comparison

Compares [metrics.md](metrics.md) (VKS in VCF 9.1, collected from a lab) with [metrics-vanilla.md](metrics-vanilla.md) (upstream Kubernetes 1.35, from the API definitions).

## In short

1. **VKS adds a management layer above the cluster.** The Supervisor, Supervisor Namespaces and Supervisor Services have no counterpart in vanilla Kubernetes. Their metrics come from vCenter and the Supervisor, not from the workload cluster.
2. **VKS makes the cluster and its node pools API objects.** In vanilla Kubernetes a cluster is only the set of objects its API server holds, so its metrics are sums and counts. In VKS, each cluster is a Cluster API `Cluster` object on the Supervisor, with desired versus actual node counts.
3. **Inside a VKS cluster, the metrics are vanilla.** Node, Namespace, Workload, Pod and Container metrics use the same upstream APIs (K8S, KS, MS) with the same field names.
4. **The Supervisor is where VKS removes metrics.** Its ESX host nodes and vSphere Pods have far fewer kubelet stats than ordinary nodes and pods, and its Metrics API is blocked.

## Object types

| Object type | Vanilla | VKS | Difference |
|---|---|---|---|
| Supervisor | — | 14 metrics | VKS only. vCenter capacity and usage (MHz, MB) plus object counts |
| Supervisor Namespace | — | 11 metrics | VKS only. vCenter usage and storage-policy quota |
| Supervisor Service | — | No metrics | VKS only. Status and properties only |
| K8s Cluster | 15 metrics, all Derived | 21 metrics | VKS adds desired, ready, available and up-to-date node counts from the `Cluster` object |
| K8s Node Pool | — | 5 metrics | VKS only (Cluster API `MachineDeployment`). Vanilla has no node pool concept |
| K8s Node | 28 metrics | 25 metrics | Same API fields. VKS limits ESX host nodes on the Supervisor |
| K8s Namespace | 8 metrics | 6 metrics | Same API fields |
| K8s Workload | 20 metrics | 14 metrics | Same API fields |
| K8s Pod | 19 metrics | 16 metrics | Same API fields. VKS limits vSphere Pods on the Supervisor |
| K8s Container | 16 metrics | 15 metrics | Same API fields. VKS limits vSphere Pod containers |

The extra rows in the vanilla column are upstream fields that VKS clusters also serve; they are not yet in `metrics.md` (see [Gaps in metrics.md](#gaps-in-metricsmd)). The real differences are the VKS-only object types and the Supervisor limits.

## Sources

| Source | Vanilla | VKS cluster | Supervisor |
|---|---|---|---|
| VC: vCenter REST API | — | — | Supervisor and Supervisor Namespace stats |
| SUP: Supervisor API | — | Cluster and node-pool counts come from here, not from the cluster itself | Node, pod and quota objects |
| K8S: Kubernetes API | Yes | Yes | Yes |
| KS: Kubelet Summary API | Yes, every node | Yes, every node | Control-plane VMs only. ESX host nodes return no node stats; vSphere Pods return a reduced set |
| MS: Metrics API | Only if metrics-server is installed | Installed | 403 for `administrator@vsphere.local` |

## Differences in detail

### 1. Cluster: counted versus declared

| Question | Vanilla | VKS |
|---|---|---|
| How many nodes exist? | Count `Node` objects | `Cluster` `status.controlPlane.replicas`, `status.workers.replicas` |
| How many nodes should exist? | Not available | `status.controlPlane.desiredReplicas`, `status.workers.desiredReplicas` |
| Are nodes on the target version? | Compare `nodeInfo.kubeletVersion` per node | `upToDateReplicas` |
| Which node pool is a node in? | Not available (labels by convention only) | `MachineDeployment` per pool, node label `vks.vmware.com/nodepool` |

Vanilla Kubernetes cannot report "desired versus actual" for nodes. A node that was never created leaves no trace. VKS can report it because the Supervisor holds the declared state.

Cluster API is an upstream Kubernetes project (SIG Cluster Lifecycle), not a VMware API. What makes VKS different is that Cluster API is always present and runs on the Supervisor, outside the workload cluster. VMware-specific parts are the ClusterClass and some cluster conditions (`AddonsReconciled`, `SystemChecksSucceeded`, `UpdatesAvailable`; see [properties.md](properties.md)).

### 2. Units: hypervisor versus Kubernetes

| Layer | CPU | Memory | Storage |
|---|---|---|---|
| Supervisor, Supervisor Namespace (VC) | MHz | MB | MB |
| Everything in Kubernetes (K8S, KS, MS) | cores, nanocores | bytes | bytes |

Supervisor CPU in MHz cannot be added to or compared with Kubernetes cores without the host's clock speed. Keep the two layers separate in dashboards.

### 3. Storage quota

| | Vanilla | VKS |
|---|---|---|
| Object | `ResourceQuota` with `requests.storage` or `<storageclass>.storageclass.storage.k8s.io/requests.storage` | `StoragePolicyQuota` on the Supervisor Namespace |
| Granularity | Per namespace, optionally per storage class | Per storage policy and per storage class, split by extension (VM, PVC, snapshot) |
| Reserved versus used | Used only | Used and reserved |

Inside a VKS cluster, `ResourceQuota` works as in vanilla Kubernetes. `StoragePolicyQuota` adds a limit across all clusters and VMs in a Supervisor Namespace.

### 4. Supervisor limits

These apply only to the Supervisor; a VKS cluster behaves like vanilla Kubernetes.

| Metric area | Vanilla node or pod | Supervisor ESX host node | vSphere Pod |
|---|---|---|---|
| Capacity (`cpu`, `memory`, `pods`) | Yes | Yes | n/a |
| Ephemeral storage, hugepages capacity | Yes | No | n/a |
| CPU usage rate (`usageNanoCores`) | Yes | No | No (pod); Yes (container) |
| CPU cumulative (`usageCoreNanoSeconds`) | Yes | No | Yes |
| Memory usage | Yes | No | Yes |
| Memory working set, RSS | Yes | No | No (pod); Yes (container) |
| Network | Yes | No | Per interface only |
| Filesystem, image FS, ephemeral storage | Yes | No | No; container root FS and logs: used only |
| Process count | Yes | No | No |
| PSI pressure | Kubernetes 1.34+ | No (Kubernetes 1.32) | No |
| Metrics API | With metrics-server | 403 | 403 |

### 5. PSI pressure

PSI is version-dependent in both. It needs Kubernetes 1.34+ and cgroup v2. VKS 3.6 clusters (1.35) have it; the VCF 9.1 Supervisor (1.32) does not.

## Gaps in metrics.md

These upstream fields are in `metrics-vanilla.md` but not in `metrics.md`. VKS clusters run upstream Kubernetes 1.35, so they should serve them, but none were checked in the lab. Most need an object the lab does not have (an HPA, a PDB, a PVC, a GPU node).

| Object Type | Metric | Why it was not seen |
|---|---|---|
| K8s Cluster | Number of Nodes, Ready / Not Ready, by role | Derivable; VKS used `Cluster` counts instead |
| K8s Cluster | Number of Persistent Volumes | Not collected |
| K8s Node | Extended Resource Capacity / Allocatable | No device plugins (GPUs) in the lab |
| K8s Node | Number of Images / Image Size, Volumes Attached | Not collected |
| K8s Namespace | Number of PVCs, PVC Storage Requested / Provisioned | Not collected |
| K8s Workload | Job Parallelism / Backoff Limit | Not collected (spec fields) |
| K8s Workload | Autoscaler (HPA) replicas and metric values | No HPA in the lab |
| K8s Workload | Disruption budget (PDB) counts | No PDB in the lab |
| K8s Pod | Pod-level Requests and Limits, Pod Overhead, Priority | Not collected (spec fields); pod-level resources need 1.34+ |
| K8s Container | Allocated / Actual Resources (in-place resize) | Not collected |

Before adding them to `metrics.md`, verify them on the lab VKS cluster. On the Supervisor (1.32), pod-level resources and PSI are not available.
