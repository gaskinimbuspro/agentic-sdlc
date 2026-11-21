# Platform bootstrap

Installs the work-server platform from Git: Argo CD, then Forgejo (Forge), Woodpecker (Cerberus), Argo Workflows (Iris's engine), Iris's workflow and one Argo CD application per project environment. Roles are explained in [the cast](../docs/architecture/cast.md).

```
platform/
  cluster/k3s.sh                    pinned, checksum-verified single-node k3s
  terraform/                        Argo CD and the root application on an existing cluster
  apps/                             Argo CD Applications, one per component (app of apps)
  components/forgejo/values.yaml    Forgejo chart values; admin secret comes from Terraform
  components/woodpecker.values.yaml Woodpecker chart values: Forgejo forge, Kubernetes backend
  components/argo-workflows.values.yaml
  components/iris/                  WorkflowTemplate, CronWorkflow (suspended), RBAC, NetworkPolicy
  images/iris/                      image for Iris's steps, built from locked wheels
  apps/projects.yaml                ApplicationSet: <project>-staging and <project>-prod from each deploy repository
  scripts/                          connect Woodpecker and Argo CD to Forgejo, protect branches, prepare a project
  templates/                        pipelines and deploy repository for a new project
```

## Install

1. On the work server: `sudo platform/cluster/k3s.sh` (run it from a systemd unit in practice).
2. `cd platform/terraform && terraform init && terraform apply -var kubeconfig_path=/etc/rancher/k3s/k3s.yaml`
3. Argo CD installs everything under `platform/apps` from `git_revision`. `terraform output -raw forgejo_admin_password` gives the Forgejo admin password; it is never stored in Git.
4. Connect Cerberus: `FORGEJO_ADMIN_PASSWORD=... scripts/connect-woodpecker.sh` creates the OAuth application and the `woodpecker-forgejo` Secret. Log in to Woodpecker once as the Forgejo admin to activate repositories.
5. Per project, release path: `scripts/setup_project.py OWNER NAME --tokens DIR` (deploy repository, release and reader identities, deploy branch protection); `scripts/protect-main.sh OWNER/NAME`; `DEPLOY_READER_TOKEN=... scripts/connect-argocd.sh`; add the project to `apps/projects.yaml`; copy [templates](templates/README.md); store the release token as the Woodpecker secret `release_token` for push events only; give the node read access to the registry.
6. Per project, Iris: create Iris's Forgejo user and token, the `iris-config` ConfigMap (Iris configuration as `iris.json`), the `iris-forgejo` Secret (`token`) and the `iris-model` Secret (`OPENAI_BASE_URL`, `OPENAI_MODEL`, `OPENAI_API_KEY`) in the `iris` namespace, then unsuspend the `iris` CronWorkflow.

`egress_proxy` and `ca_bundle_path`, and in `k3s.sh` `ALLOW_CGROUP_V1` and `RESTRICT_OOM_SCORE_ADJ`, exist only for restricted hosts such as the sandbox used for the trial below. Leave them unset on a normal server.

## What was tested, and where

On 20 and 21 November 2026, inside a temporary cloud sandbox (4 CPUs, 15 GB, cgroup v1, all traffic through a TLS-inspecting proxy), not on a production server:

| Item | Result |
| --- | --- |
| kind | Failed: nested containers could not start pods in that sandbox. Replaced by k3s on the host. |
| k3s v1.37.2+k3s1 | Ran after allowing cgroup v1 and restricting `oom_score_adj` (sandbox limits). |
| Terraform 1.17.2 (helm 3.3.0, kubernetes 3.5.0, random 3.9.1) | `apply` installed Argo CD (chart 10.18.2, v3.6.2) and the root application in 41 s. |
| Argo CD sync | First run: all six applications Synced and Healthy: Forgejo 15.0.12 (chart 17.3.3), Tekton Pipelines v1.18.0 and Triggers v0.38.0, Argo Workflows v4.1.6 (chart 2.0.18), Iris. Tekton reported Degraded until metrics-server ran. Second run (21 November): Tekton replaced by Woodpecker; eight applications Synced and Healthy, including `demo-staging` and `demo-prod`. |
| Forgejo | API answered; login with the Terraform-generated admin password worked; a bot user with a scoped token pushed over HTTP with a token header. |
| Iris on Argo Workflows, stand-in builder | Issue "greeting": pull request opened with two files. Issue "farewell": first attempt failed checks, repair round fixed it, pull request opened. Issue "clean up tests": blocked with "builder removed or edited existing tests", nothing pushed. Each run took 60 to 95 s. |
| Found and fixed during the trial | A token secret with a trailing newline failed, and the resulting error message contained the token. Iris now strips and validates the token and never echoes request errors; the exposed trial token was revoked. Deleting tests is now stopped right after the build instead of after a wasted repair round. |
| NetworkPolicy for the builder | **Not demonstrated.** The policy and its firewall rules were created, but that sandbox's kernel did not pass pod traffic through iptables, so the builder could still reach Forgejo. Verify on the real server: a pod labelled `iris.agentic-sdlc/role=builder` in `iris` must fail to reach `forgejo-http.forgejo.svc`. The builder still holds no git token and its checkout has no usable remote. |
| Real model and Qwen Code | Not tested; the builder was a deterministic stand-in script. |
| Tekton | Installed in the first trial run, then removed: the product owner chose Woodpecker for CI. |
| Woodpecker 3.20.1 (chart 3.7.7), 21 November | Installed by Argo CD; connected to Forgejo with `connect-woodpecker.sh`; login through Forgejo OAuth; repository activated, webhook created by Woodpecker. The agent needs `WOODPECKER_BACKEND_K8S_STORAGE_RWX=false` on a single node with `local-path` storage, and a persisted `WOODPECKER_GRPC_SECRET` so agents survive server restarts. |
| Pull-request gate | Status `ci/woodpecker/pr/checks` appeared on each pull request. A failing check blocked the merge even after approval; an unapproved pull request could not be merged; Iris's bot could not push to main. With approval alone the bot could still merge, so `protect-main.sh` also restricts merging to the product owner; after that the bot's merge was refused and the owner's succeeded. |
| Pipeline errors | A YAML mistake in the release pipeline turned the pull-request status to error and blocked the merge. Commands containing `: ` must be quoted; shell variables need `$$`. The template uses one script block. |
| Release to staging | After the owner's merge: `checks` passed on main, kaniko (plugin-kaniko, osscontainertools fork 2.3.5) built the image and pushed it to Forgejo's registry, the digest was written to the staging overlay, Argo CD synced, and the running pod's image ID equalled that digest. A second change (v2) reached staging 12 s after the Argo CD refresh while prod kept the approved digest. |
| Prod promotion | The release bot's push to the prod overlay was refused; its pull request could not be merged by the bot or without approval; after the owner's approval and merge, Argo CD synced prod to the staging digest. |
| Secret scope | A pull request that tried to read `release_token` was refused by Woodpecker: "secret is not allowed to be used with pipeline event pull_request". |
| Token rotation | Re-running `setup_project.py` rotated both bot tokens; after updating Argo CD, Woodpecker and the node registry configuration, the next release worked end to end. |
| Sandbox-only workarounds | Pods could not reach Docker Hub, so the Python base image was mirrored into Forgejo's registry once and referenced by digest. k3s restarted under `umask 077` created containers whose root directory was mode 0700, so non-root images failed with "Permission denied"; start k3s with umask 022. The node registry credentials live in `/etc/rancher/k3s/registries.yaml`, outside Git. |
| Not done | Pull-request previews, migration pre-sync jobs, a secrets manager, a staging smoke test before the prod pull request, TLS for the registry (the trial used plain HTTP inside the cluster), and Iris opening a pull request with a real model. |
| gVisor | Not tried. |
