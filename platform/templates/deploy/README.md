# NAME-deploy

Desired state for OWNER/NAME. Argo CD syncs `overlays/staging` and
`overlays/prod`. The release pipeline sets the staging image digest after every
merge to main of the source repository. Production changes only by pull request
approved by the product owner.
