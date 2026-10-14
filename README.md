# VKS Observability
Kubernetes monitoring and troubleshooting in Broadcom VMware Cloud Foundation 9

## Object model

Ten object types, taken from the live APIs of a VCF 9.1 lab (vCenter REST API, Supervisor Kubernetes API v1.32, VKS 3.6 cluster Kubernetes API v1.35). vSphere objects (VM, resource pool, ESX host, datastore) are out of scope.

| # | Object type | Lives in | Parent |
|---|---|---|---|
| 1 | Supervisor | vCenter / Supervisor | (vSphere cluster) |
| 2 | Supervisor Namespace (vSphere Namespace) | Supervisor | Supervisor |
| 3 | Supervisor Service | Supervisor | Supervisor |
| 4 | K8s Cluster (VKS cluster) | Supervisor Namespace | Supervisor Namespace |
| 5 | K8s Node Pool | VKS cluster | K8s Cluster |
| 6 | K8s Node | Supervisor and VKS cluster | K8s Cluster / Node Pool, or Supervisor |
| 7 | K8s Namespace | Supervisor and VKS cluster | K8s Cluster |
| 8 | K8s Workload (Deployment, StatefulSet, DaemonSet, ReplicaSet, Job, CronJob) | Supervisor and VKS cluster | K8s Namespace |
| 9 | K8s Pod | Supervisor (vSphere Pod) and VKS cluster | K8s Workload / Namespace, K8s Node |
| 10 | K8s Container | Supervisor and VKS cluster | K8s Pod |

K8s Workload is one object type with a Workload Type property. K8s Container is not a Kubernetes API object; it is an entry inside a Pod.

| Document | Content |
|---|---|
| [metrics.md](metrics.md) | Numeric attributes per object type, with unit, source API and API field |
| [properties.md](properties.md) | Non-numeric attributes per object type, with source API, API field and values |
| [raw/](raw/) | Field-name lists collected from the live APIs (paths only, no values or instance names) |
