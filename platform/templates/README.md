# Project templates

Files a new project copies, tested end to end in the [platform trial](../README.md#what-was-tested-and-where). Replace `OWNER`, `NAME` and `BASE` (the mirrored base image) before use.

| Path | Goes to | Purpose |
| --- | --- | --- |
| `source/.woodpecker/checks.yaml` | the source repository | Required pull-request check; runs the repository's own check script. Its status context `ci/woodpecker/pr/checks` is what branch protection requires. |
| `source/.woodpecker/release.yaml` | the source repository | After `checks` passes on main: build the image once with kaniko, record the digest, write it into the staging overlay of the deploy repository. |
| `source/Dockerfile` | the source repository | Pattern only: base image from the internal registry, pinned by digest, non-root user. |
| `deploy/` | `OWNER/NAME-deploy` | Desired state: `base/` plus `overlays/staging` and `overlays/prod`. Argo CD syncs both through the [projects ApplicationSet](../apps/projects.yaml). |

Who may change what:

| Change | Who | Enforced by |
| --- | --- | --- |
| Source main | Merge of a pull request with a passing check, approved and merged by the product owner | Forgejo branch protection ([protect-main.sh](../scripts/protect-main.sh)) |
| Staging digest | `release-bot`, from the release pipeline on main only | Deploy repository protection: only `overlays/staging/kustomization.yaml` may be pushed directly; the Woodpecker secret `release_token` is limited to push events |
| Prod digest and everything else in the deploy repository | Pull request approved and merged by the product owner | Deploy repository protection ([setup_project.py](../scripts/setup_project.py)) |
| The cluster | Argo CD only | Nobody else holds cluster credentials; agents never do |
