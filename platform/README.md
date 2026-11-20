# Platform bootstrap

Installs the work-server platform from Git: Argo CD, then Forgejo (Forge), Tekton Pipelines and Triggers (Cerberus), Argo Workflows (Iris's engine) and Iris's workflow. Roles are explained in [the cast](../docs/architecture/cast.md).

```
platform/
  cluster/k3s.sh                    pinned, checksum-verified single-node k3s
  terraform/                        Argo CD and the root application on an existing cluster
  apps/                             Argo CD Applications, one per component (app of apps)
  components/forgejo/values.yaml    Forgejo chart values; admin secret comes from Terraform
  components/tekton/                pinned Tekton release manifests
  components/argo-workflows.values.yaml
  components/iris/                  WorkflowTemplate, CronWorkflow (suspended), RBAC, NetworkPolicy
  images/iris/                      image for Iris's steps, built from locked wheels
```

## Install

1. On the work server: `sudo platform/cluster/k3s.sh` (run it from a systemd unit in practice).
2. `cd platform/terraform && terraform init && terraform apply -var kubeconfig_path=/etc/rancher/k3s/k3s.yaml`
3. Argo CD installs everything under `platform/apps` from `git_revision`. `terraform output -raw forgejo_admin_password` gives the Forgejo admin password; it is never stored in Git.
4. Per project: create Iris's Forgejo user and token, the `iris-config` ConfigMap (Iris configuration as `iris.json`), the `iris-forgejo` Secret (`token`) and the `iris-model` Secret (`OPENAI_BASE_URL`, `OPENAI_MODEL`, `OPENAI_API_KEY`) in the `iris` namespace, then unsuspend the `iris` CronWorkflow.

`egress_proxy` and `ca_bundle_path`, and in `k3s.sh` `ALLOW_CGROUP_V1` and `RESTRICT_OOM_SCORE_ADJ`, exist only for restricted hosts such as the sandbox used for the trial below. Leave them unset on a normal server.

## What was tested, and where

On 20 November 2026, inside a temporary cloud sandbox (4 CPUs, 15 GB, cgroup v1, all traffic through a TLS-inspecting proxy), not on a production server:

| Item | Result |
| --- | --- |
| kind | Failed: nested containers could not start pods in that sandbox. Replaced by k3s on the host. |
| k3s v1.37.2+k3s1 | Ran after allowing cgroup v1 and restricting `oom_score_adj` (sandbox limits). |
| Terraform 1.17.2 (helm 3.3.0, kubernetes 3.5.0, random 3.9.1) | `apply` installed Argo CD (chart 10.18.2, v3.6.2) and the root application in 41 s. |
| Argo CD sync | All six applications Synced and Healthy: Forgejo 15.0.12 (chart 17.3.3), Tekton Pipelines v1.18.0 and Triggers v0.38.0, Argo Workflows v4.1.6 (chart 2.0.18), Iris. Tekton reported Degraded until metrics-server ran, because its webhook autoscaler needs CPU metrics. |
| Forgejo | API answered; login with the Terraform-generated admin password worked; a bot user with a scoped token pushed over HTTP with a token header. |
| Iris on Argo Workflows, stand-in builder | Issue "greeting": pull request opened with two files. Issue "farewell": first attempt failed checks, repair round fixed it, pull request opened. Issue "clean up tests": blocked with "builder removed or edited existing tests", nothing pushed. Each run took 60 to 95 s. |
| Found and fixed during the trial | A token secret with a trailing newline failed, and the resulting error message contained the token. Iris now strips and validates the token and never echoes request errors; the exposed trial token was revoked. Deleting tests is now stopped right after the build instead of after a wasted repair round. |
| NetworkPolicy for the builder | **Not demonstrated.** The policy and its firewall rules were created, but that sandbox's kernel did not pass pod traffic through iptables, so the builder could still reach Forgejo. Verify on the real server: a pod labelled `iris.agentic-sdlc/role=builder` in `iris` must fail to reach `forgejo-http.forgejo.svc`. The builder still holds no git token and its checkout has no usable remote. |
| Real model and Qwen Code | Not tested; the builder was a deterministic stand-in script. |
| Tekton pull-request check | Not built yet: Tekton is installed, but no Forgejo webhook, pipeline or commit-status reporting exists. Pull requests are therefore not yet gated by Cerberus. |
| gVisor | Not tried. |
