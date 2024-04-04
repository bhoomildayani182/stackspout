# Stackspin Outwards - Stackspout

This repository extends [Stackspin](https://open.greenhost.net/stackspin/stackspin)
with extra applications and overrides
focused on business use.
Once stabilized, the aim is to contribute as much upstream as possible.

Stackspout is used in day-to-day business
with a double-digit user number,
so all experiments happen carefully.
Still, it is an experimental offering.

## Tools

Useful tools for administration:
- my `stack` CLI helper, currently part of my dotfiles:
  https://git.jfischer.org/xeruf/dotfiles/src/branch/main/.config/shell/server#L11
- stackspin docs:
  https://docs.stackspin.net/en/v2/system_administration/customizing.html

## Explanation - Typical App Deployment in Stackspout with Flux on Kubernetes

The diagram illustrates generically how continuous app deployment works in our Kubernetes cluster
from Infrastructure-as-Code using flux.
Not every app has database, backend and frontend,
but in the end the deployments all work very similarly
so there is no point showing it for each individual app.
Except for the Single-Sign On,
apps also do not really depend on each other.

Explanations:
- deploy :: creates a resource on the cluster from a file in the GitRepository
- create :: creates a resource on the cluster using Kubernetes logic
- ... all :: creates multiple independent resources

All Flux Kustomizations refer to a directory in the GitRepository,
but for clarity I omitted it beyond the initial one.

Clouds are created not via Flux GitOps,
but through one-time scripts.

![Flux Diagram](./stackspout.png)

### Guide: Creating OAuth Credentials for an external service
- push an OAuth2Client definition like for the apps,
  adjusting `metadata.name` and `spec.secretName` as well as `spec.redirectUris`
- obtain the generated `client_secret` for your application from kubernetes:

      kubectl get secret -n flux-system stackspin-APP-oauth-variables --template '{{.data.client_secret}}' | base64 -d

  with client_id:

      kubectl get secret -n flux-system stackspin-APP-oauth-variables --template '{{.data.client_id}}{{"\n"}}{{.data.client_secret}}{{"\n"}}' | while read in; do echo $in | base64 -d; echo; done


## Customizations

### Overrides
- Adds many Nextcloud extensions and some configuration
  -> most notably `external` to add Applications into Nextcloud as hub
- Add Email Auth back to Zulip so guests can be invited

### New Applications
below list is formatted as:
> subdomain: Service (helmrepo, if not provided by the service authors)

#### Stable including Single-Sign-On
- dev: Gitea (TODO: Forgej)
- do: Vikunja (k8s-at-home - migrating to creators chart)
- ninja: InvoiceNinja (No SSO)
#### In Development
- people: SuiteCRM (bitnami repo)
- time: Kimai (robjuz repo)
#### Planned
- meet: Jitsi Meet
- wiki: Wiki (maybe wikijs, but I'd like something that integrated with Nextcloud and Markdown/Orgdown)
#### Ideas
- link: URL Shortener
- connect: Bonfire

### Issues to Tackle
- generate_secrets.py was copied from Stackpin
  -> new mechanism
#### Functionally
- Nextcloud too slow - add Redis?
- Preconfigure user settings in Nextcloud, Vikunja and more

## Setup

> Warning: Lots of experiments happening here!

First [install Stackspin](https://docs.stackspin.net/en/latest/installation/install_stackspin.html).
Then apply the configuration to your cluster:

```sh
install.sh
```

Done!
Note that the added applications are currently only toggled via repository changes
and integration with Stackspin mechanisms is very rudimentary.
To list the central resource related to this repo:

```sh
kubectl get gitrepositories -A
kubectl get kustomization -A -o=jsonpath='{.items[?(@.spec.sourceRef.name=="stackspout")].metadata.name}'
kubectl -n stackspout get helmreleases
kubectl -n stackspout get pods
```

But there are also ConfigMaps, Secrets, StatefulSets, PVCs, Helmrepos and more...
