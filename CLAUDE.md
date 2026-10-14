# VKS Observability

Defines the object model (object types, metrics, properties) for monitoring Kubernetes in VCF 9: the Supervisor and VKS workload clusters. The model is built from what the live APIs actually return, so it can be checked against the VMware manual.

## Files

- `metrics.md`: one table, `Object Type | Metric | Unit | Source | API field | Notes`.
- `metrics-vanilla.md`: same format, for upstream Kubernetes 1.35 with no vendor APIs. Built from the upstream API definitions, not from the lab.
- `metrics-comparison.md`: VKS versus vanilla. Update it when either metrics file changes.
- `properties.md`: one table, `Object Type | Property | Source | API field | Values / notes`.
- `raw/`: field-path lists dumped from the lab. `fields.json` and `fields2.json` hold numeric paths (metric candidates); `props_fields.json` holds non-numeric paths (property candidates).

Keep both tables in the same format and object-type order (the 10 types in `README.md`). Use the same source codes: VC, SUP, K8S, KS, MS, Derived.

## Rules

- Every metric or property must cite the API field it comes from. A field not seen live is marked *(schema)* (metrics) or listed under "Not seen in the lab" (properties).
- No instance names, IP addresses, hostnames or values in the repo: field paths only. The repo has a GitHub remote, so anything committed is published.
- Condition names are the ones the lab returned, not the ones in the documentation.

## Lab

- VCF 9.1. Supervisor Kubernetes v1.32. One VKS cluster on Kubernetes v1.35 (VKS 3.6, ClusterClass `builtin-generic-v3.6.0`, Cluster API `v1beta2`), one control-plane and one worker node.
- Access: vCenter REST API session; Supervisor API token from `POST https://<supervisor>/wcp/login` with `administrator@vsphere.local`; VKS kubeconfig from Supervisor secret `<namespace>/<cluster>-kubeconfig`.
- Collection scripts are in `tools/`. `tools/lab.py` builds read-only clients `V` (vCenter), `S` (Supervisor) and `G` (VKS cluster, `None` if it doesn't exist). `fields.py` and `fields2.py` write the numeric path lists and `props.py` the non-numeric ones into `raw/`; `conds.py` prints condition types and phases per kind.
- All lab values (`VC_HOST`, `SUP_HOST`, `VC_USER`, `VCPW`, `VKS_NS`, `VKS_CLUSTER`) are environment variables loaded from the git-ignored `.secrets/lab.env`. Scripts must never hard-code them. To run, from the repo root in PowerShell: `. tools/env.ps1` then `python tools/conds.py`.
- The full API dumps from the first pass are in the sibling repo `../VCF-vCommunity-Adapter/.lab/` (git-ignored there) and are not copied here because they contain instance names.

## Open items

- Supervisor Namespace CPU and memory limits (`resource_spec`): not set in the lab, field names not verified.
- `ZoneResourceUtilization` returned 403; not in the model.
- Fields marked *(schema)* need a lab state where they are non-zero to be verified.
- The lab VKS cluster created for this work (`VKS_CLUSTER` in `VKS_NS`, see `.secrets/lab.env`) still exists. `G` needs it, so delete it only when no more VKS-side collection is planned.
