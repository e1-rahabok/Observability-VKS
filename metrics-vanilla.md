# Vanilla Kubernetes Object Metrics

Metrics (numeric attributes) for each object type in upstream Kubernetes (v1.35), with no vendor-specific APIs: no vCenter, no Supervisor and no Cluster API. It is the baseline for [metrics.md](metrics.md) (VKS); [metrics-comparison.md](metrics-comparison.md) compares the two.

Unlike `metrics.md`, this table was not collected from a lab. Field names come from the upstream API definitions: the Kubernetes API reference (`core/v1`, `apps/v1`, `batch/v1`, `autoscaling/v2`, `policy/v1`), the Kubelet Summary API types (`k8s.io/kubelet/pkg/apis/stats/v1alpha1`) and the Metrics API types (`k8s.io/metrics/pkg/apis/metrics/v1beta1`).

**Source legend**

| Code | API |
|---|---|
| K8S | Kubernetes API server of the cluster (core, `apps/v1`, `batch/v1`, `autoscaling/v2`, `policy/v1`) |
| KS | Kubelet Summary API: `/api/v1/nodes/<node>/proxy/stats/summary` through the API server. Needs RBAC on `nodes/proxy` |
| MS | Metrics API `metrics.k8s.io/v1beta1`. Served only when the metrics-server add-on (kubernetes-sigs) is installed; kubeadm does not install it |
| Derived | Counted, summed or computed from other fields |

Conventions are the same as in [metrics.md](metrics.md): KS fields are relative to `node.*`, `pods[].*` or `containers[].*`; KS CPU has a rate (`usageNanoCores`) and a cumulative counter (`usageCoreNanoSeconds`); Kubernetes omits status fields whose value is zero.

| Object Type | Metric | Unit | Source | API field | Notes |
|---|---|---|---|---|---|
| K8s Cluster | Number of Nodes | count | Derived | K8S `Node` | |
| K8s Cluster | Number of Nodes Ready / Not Ready | count | Derived | `Node` `conditions[type=Ready]` | |
| K8s Cluster | Number of Control Plane Nodes | count | Derived | Nodes with `labels[node-role.kubernetes.io/control-plane]` | kubeadm label. Hosted control planes have no control-plane Nodes |
| K8s Cluster | Number of Worker Nodes | count | Derived | Nodes without the control-plane label | |
| K8s Cluster | Number of Namespaces | count | Derived | K8S `Namespace` | |
| K8s Cluster | Number of Workloads (by type) | count | Derived | K8S `apps/v1`, `batch/v1` kinds | |
| K8s Cluster | Number of Pods (by phase) | count | Derived | K8S `Pod` `status.phase` | |
| K8s Cluster | Number of Containers | count | Derived | K8S `Pod` `spec.containers[]` | |
| K8s Cluster | Number of Persistent Volumes (by phase) | count | Derived | K8S `PersistentVolume` `status.phase` | |
| K8s Cluster | CPU Capacity / Allocatable | cores | Derived | Σ Node `status.capacity.cpu`, `status.allocatable.cpu` | |
| K8s Cluster | Memory Capacity / Allocatable | bytes | Derived | Σ Node `status.capacity.memory`, `status.allocatable.memory` | |
| K8s Cluster | Pod Capacity | count | Derived | Σ Node `status.allocatable.pods` | |
| K8s Cluster | CPU Usage | cores | Derived | Σ Node CPU usage (MS or KS) | |
| K8s Cluster | Memory Usage (working set) | bytes | Derived | Σ Node memory working set (MS or KS) | |
| K8s Cluster | CPU / Memory Requests, Limits | cores / bytes | Derived | Σ container `resources.requests`, `resources.limits` | |
| K8s Node | CPU Capacity / Allocatable | cores | K8S | `Node` `status.capacity.cpu`, `status.allocatable.cpu` | |
| K8s Node | Memory Capacity / Allocatable | bytes | K8S | `status.capacity.memory`, `status.allocatable.memory` | |
| K8s Node | Pod Capacity / Allocatable | count | K8S | `status.capacity.pods`, `status.allocatable.pods` | |
| K8s Node | Ephemeral Storage Capacity / Allocatable | bytes | K8S | `status.capacity.ephemeral-storage`, `status.allocatable.ephemeral-storage` | |
| K8s Node | Hugepages Capacity / Allocatable | bytes | K8S | `status.capacity.hugepages-<size>`, `status.allocatable.hugepages-<size>` | |
| K8s Node | Extended Resource Capacity / Allocatable | count | K8S | `status.capacity.<domain>/<resource>`, `status.allocatable.<domain>/<resource>` | Advertised by device plugins, for example GPUs |
| K8s Node | Number of Images / Image Size | count / bytes | Derived | `status.images[]`, Σ `status.images[].sizeBytes` | |
| K8s Node | Number of Volumes Attached | count | Derived | `status.volumesAttached[]` | |
| K8s Node | CPU Usage | nanocores | KS | `node.cpu.usageNanoCores` | |
| K8s Node | CPU Usage (cumulative) | ns | KS | `node.cpu.usageCoreNanoSeconds` | |
| K8s Node | CPU Usage | cores | MS | `NodeMetrics` `usage.cpu` | metrics-server add-on |
| K8s Node | Memory Usage | bytes | KS | `node.memory.usageBytes` | |
| K8s Node | Memory Working Set | bytes | KS / MS | `node.memory.workingSetBytes`; `NodeMetrics` `usage.memory` | MS: metrics-server add-on |
| K8s Node | Memory RSS | bytes | KS | `node.memory.rssBytes` | |
| K8s Node | Memory Available | bytes | KS | `node.memory.availableBytes` | |
| K8s Node | Memory Page Faults / Major Page Faults | count | KS | `node.memory.pageFaults`, `.majorPageFaults` | |
| K8s Node | Swap Usage / Available | bytes | KS | `node.swap.swapUsageBytes`, `.swapAvailableBytes` | |
| K8s Node | Network Received / Transmitted | bytes | KS | `node.network.rxBytes`, `.txBytes` (also per `interfaces[]`) | |
| K8s Node | Network Receive / Transmit Errors | count | KS | `node.network.rxErrors`, `.txErrors` | |
| K8s Node | Filesystem Capacity / Used / Available | bytes | KS | `node.fs.capacityBytes`, `.usedBytes`, `.availableBytes` | |
| K8s Node | Filesystem Inodes / Used / Free | count | KS | `node.fs.inodes`, `.inodesUsed`, `.inodesFree` | |
| K8s Node | Image FS Capacity / Used / Available (+ inodes) | bytes | KS | `node.runtime.imageFs.*` | |
| K8s Node | Container FS Capacity / Used / Available (+ inodes) | bytes | KS | `node.runtime.containerFs.*` | |
| K8s Node | Processes Running / Max PIDs | count | KS | `node.rlimit.curproc`, `.maxpid` | |
| K8s Node | CPU / Memory / IO Pressure (PSI) | % / µs | KS | `node.{cpu,memory,io}.psi.*` | Kubernetes 1.34+ (`KubeletPSI`, beta), cgroup v2 nodes only |
| K8s Node | System Container CPU / Memory | nanocores / bytes | KS | `node.systemContainers[].cpu.*`, `.memory.*` | kubelet, runtime, pods |
| K8s Node | Number of Pods | count | Derived | Pods with `spec.nodeName` = node | |
| K8s Node | CPU / Memory Requests, Limits | cores / bytes | Derived | Σ container `resources` of pods on the node | |
| K8s Namespace | Number of Pods / Containers / Workloads | count | Derived | K8S objects in the namespace | |
| K8s Namespace | CPU Usage | cores | Derived | Σ pod CPU (MS or KS) | |
| K8s Namespace | Memory Usage (working set) | bytes | Derived | Σ pod memory (MS or KS) | |
| K8s Namespace | CPU / Memory Requests, Limits | cores / bytes | Derived | Σ container `resources` | |
| K8s Namespace | Quota Hard (per resource) | per resource | K8S | `ResourceQuota` `status.hard.<resource>` | |
| K8s Namespace | Quota Used (per resource) | per resource | K8S | `ResourceQuota` `status.used.<resource>` | |
| K8s Namespace | Number of PVCs (by phase) | count | Derived | `PersistentVolumeClaim` `status.phase` | |
| K8s Namespace | PVC Storage Requested / Provisioned | bytes | Derived | Σ PVC `spec.resources.requests.storage`, Σ `status.capacity.storage` | |
| K8s Workload | Desired | count | K8S | Deployment, StatefulSet, ReplicaSet `spec.replicas`; DaemonSet `status.desiredNumberScheduled`; Job `spec.completions` | Not CronJob |
| K8s Workload | Current | count | K8S | Deployment, ReplicaSet `status.replicas`; StatefulSet `status.replicas`, `status.currentReplicas`; DaemonSet `status.currentNumberScheduled`; Job `status.active`; CronJob count of `status.active[]` | |
| K8s Workload | Ready | count | K8S | Deployment, StatefulSet, ReplicaSet `status.readyReplicas`; DaemonSet `status.numberReady`; Job `status.ready` | Not CronJob |
| K8s Workload | Available | count | K8S | Deployment, StatefulSet, ReplicaSet `status.availableReplicas`; DaemonSet `status.numberAvailable` | |
| K8s Workload | Unavailable | count | K8S | Deployment `status.unavailableReplicas`; DaemonSet `status.numberUnavailable` | |
| K8s Workload | Updated | count | K8S | Deployment, StatefulSet `status.updatedReplicas`; DaemonSet `status.updatedNumberScheduled` | |
| K8s Workload | Terminating | count | K8S | Deployment, ReplicaSet `status.terminatingReplicas`; Job `status.terminating` | |
| K8s Workload | Misscheduled | count | K8S | DaemonSet `status.numberMisscheduled` | |
| K8s Workload | Fully Labeled | count | K8S | ReplicaSet `status.fullyLabeledReplicas` | |
| K8s Workload | Succeeded / Failed | count | K8S | Job `status.succeeded`, `status.failed` | |
| K8s Workload | Parallelism / Backoff Limit | count | K8S | Job `spec.parallelism`, `spec.backoffLimit` | Configured limits |
| K8s Workload | Collision Count | count | K8S | Deployment, StatefulSet, DaemonSet `status.collisionCount` | |
| K8s Workload | Autoscaler Current / Desired Replicas | count | K8S | `HorizontalPodAutoscaler` `status.currentReplicas`, `status.desiredReplicas` | Workloads targeted by an HPA |
| K8s Workload | Autoscaler Min / Max Replicas | count | K8S | `HorizontalPodAutoscaler` `spec.minReplicas`, `spec.maxReplicas` | |
| K8s Workload | Autoscaler Current Metric Value | per metric | K8S | `HorizontalPodAutoscaler` `status.currentMetrics[]` | For example `resource.current.averageUtilization` |
| K8s Workload | Disruptions Allowed | count | K8S | `PodDisruptionBudget` `status.disruptionsAllowed` | Workloads covered by a PDB |
| K8s Workload | Healthy Pods Current / Desired / Expected | count | K8S | `PodDisruptionBudget` `status.currentHealthy`, `status.desiredHealthy`, `status.expectedPods` | |
| K8s Workload | Number of Pods | count | Derived | Pods owned by the workload | All workload types |
| K8s Workload | CPU / Memory Usage | cores / bytes | Derived | Σ pod usage (MS or KS) | All workload types |
| K8s Workload | CPU / Memory Requests, Limits | cores / bytes | Derived | Σ container `resources` of its pods | All workload types |
| K8s Pod | CPU Usage | nanocores | KS | `pods[].cpu.usageNanoCores` | |
| K8s Pod | CPU Usage (cumulative) | ns | KS | `pods[].cpu.usageCoreNanoSeconds` | |
| K8s Pod | CPU Usage | cores | MS | `PodMetrics` Σ `containers[].usage.cpu` | metrics-server add-on |
| K8s Pod | Memory Usage | bytes | KS | `pods[].memory.usageBytes` | |
| K8s Pod | Memory Working Set / RSS / Available | bytes | KS | `pods[].memory.workingSetBytes`, `.rssBytes`, `.availableBytes` | |
| K8s Pod | Memory Page Faults / Major Page Faults | count | KS | `pods[].memory.pageFaults`, `.majorPageFaults` | |
| K8s Pod | Swap Usage | bytes | KS | `pods[].swap.swapUsageBytes` | |
| K8s Pod | Network Received / Transmitted | bytes | KS | `pods[].network.rxBytes`, `.txBytes` (+ `interfaces[]`) | |
| K8s Pod | Network Receive / Transmit Errors | count | KS | `pods[].network.rxErrors`, `.txErrors` | |
| K8s Pod | Ephemeral Storage Capacity / Used / Available (+ inodes) | bytes | KS | `pods[].ephemeral-storage.*` | |
| K8s Pod | Volume Capacity / Used / Available (+ inodes), per volume | bytes | KS | `pods[].volume[].capacityBytes`, `.usedBytes`, `.availableBytes`, `.inodes*` | Includes PVCs (`volume[].pvcRef`) |
| K8s Pod | Number of Processes | count | KS | `pods[].process_stats.process_count` | |
| K8s Pod | CPU / Memory / IO Pressure (PSI) | % / µs | KS | `pods[].{cpu,memory,io}.psi.*` | Kubernetes 1.34+, cgroup v2 nodes only |
| K8s Pod | Number of Containers | count | Derived | `spec.containers[]` | |
| K8s Pod | Container Restarts (total) | count | Derived | Σ `status.containerStatuses[].restartCount`, `status.initContainerStatuses[].restartCount` | |
| K8s Pod | CPU / Memory Requests, Limits | cores / bytes | Derived | Σ `spec.containers[].resources.requests`, `.limits` | |
| K8s Pod | Pod-level CPU / Memory Requests, Limits | cores / bytes | K8S | `spec.resources.requests`, `spec.resources.limits` | `PodLevelResources` (beta from 1.34) |
| K8s Pod | Pod Overhead | cores / bytes | K8S | `spec.overhead.cpu`, `spec.overhead.memory` | Set by the pod's RuntimeClass |
| K8s Pod | Priority | number | K8S | `spec.priority` | From the PriorityClass |
| K8s Container | CPU Usage | nanocores | KS | `containers[].cpu.usageNanoCores` | |
| K8s Container | CPU Usage (cumulative) | ns | KS | `containers[].cpu.usageCoreNanoSeconds` | |
| K8s Container | CPU Usage | cores | MS | `PodMetrics` `containers[].usage.cpu` | metrics-server add-on |
| K8s Container | Memory Usage | bytes | KS | `containers[].memory.usageBytes` | |
| K8s Container | Memory Working Set | bytes | KS / MS | `containers[].memory.workingSetBytes`; `PodMetrics` `containers[].usage.memory` | MS: metrics-server add-on |
| K8s Container | Memory RSS / Available | bytes | KS | `containers[].memory.rssBytes`, `.availableBytes` | |
| K8s Container | Memory Page Faults / Major Page Faults | count | KS | `containers[].memory.pageFaults`, `.majorPageFaults` | |
| K8s Container | Swap Usage / Available | bytes | KS | `containers[].swap.swapUsageBytes`, `.swapAvailableBytes` | |
| K8s Container | Root FS Capacity / Used / Available (+ inodes) | bytes | KS | `containers[].rootfs.*` | |
| K8s Container | Log FS Capacity / Used / Available (+ inodes) | bytes | KS | `containers[].logs.*` | |
| K8s Container | CPU / Memory / IO Pressure (PSI) | % / µs | KS | `containers[].{cpu,memory,io}.psi.*` | Kubernetes 1.34+, cgroup v2 nodes only |
| K8s Container | Restart Count | count | K8S | `Pod` `status.containerStatuses[].restartCount` | |
| K8s Container | Last Exit Code | code | K8S | `status.containerStatuses[].lastState.terminated.exitCode` | |
| K8s Container | CPU Request / Limit | cores | K8S | `spec.containers[].resources.requests.cpu`, `.limits.cpu` | |
| K8s Container | Memory Request / Limit | bytes | K8S | `spec.containers[].resources.requests.memory`, `.limits.memory` | |
| K8s Container | Allocated / Actual Resources | cores / bytes | K8S | `status.containerStatuses[].allocatedResources`, `status.containerStatuses[].resources` | In-place pod resize; differ from spec while a resize is in progress |

## Notes

- **No Cluster object.** Core Kubernetes has no API object for the cluster itself, so every cluster metric is derived from Nodes and other objects. There are no node pools either: grouping nodes into pools is done by a provisioner (Cluster API, a cloud provider, or labels).
- **No layer above the cluster.** There is nothing like a Supervisor, Supervisor Namespace or Supervisor Service, and no hypervisor-level stats.
- **The metrics pipeline is an add-on.** The Kubelet Summary API is built into every kubelet. The Metrics API needs metrics-server, which many installers (including kubeadm) do not deploy.
- **The control plane may be invisible.** With kubeadm, control-plane components run as static pods on control-plane Nodes and appear in the tables above. With a hosted control plane they are not Nodes or Pods in the cluster.
- **Outside this model.** Every kubelet and control-plane component also serves Prometheus metrics: kubelet `/metrics`, `/metrics/resource`, `/metrics/cadvisor`, `/metrics/probes`; API server, scheduler, controller manager and etcd `/metrics`. kube-state-metrics (a SIG Instrumentation add-on) turns object fields into Prometheus series. These are text-format time series, not API fields, so they are not listed here.
