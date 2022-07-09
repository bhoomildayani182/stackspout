# Stackspin Outwards - Stackspout

This repository extends [Stackspin](https://open.greenhost.net/stackspin/stackspin)
with extra applications and overrides
to make it more commercially/professionally interesting.
Once stabilized, the aim is to contribute as much upstream as possible.

Stackspout is used in day-to-day business
with a 2-digit user number,
so all experiments happen carefully.

## Customizations

### Overrides
- Adds many Nextcloud extensions and some configuration
- Add Email Auth back to Zulip

### New Applications
> subdomain: Service (helmrepo, if not provided by the service authors)
#### Stable including Single-Sign-On
- dev: Gitea 
- do: Vikunja (k8s-at-home)
#### In Development
- people: SuiteCRM (bitnami repo)
- time: Kimai (robjuz repo)
#### Planned
- meet: Jitsi Meet
- wiki: Wiki (maybe wikijs, but I'd like something that integrated with Nextcloud and Markdown/Orgdown)
#### Ideas
- link: URL Shortener
- Bonfire

### Issues to tackle
#### Structurally
- generate_secrets.py was copied from Stackpin
- all apps except gitea lack pvcs
#### Functionally
- Nextcloud too slow - add Redis
- Preconfigure user settings in Nextcloud, Vikunja and more

## Installation

> Warning: Lots of experiments happening here!

Apply it to your cluster:

```sh
basic/install.sh
```

List the resource related to this repo:

```sh
kubectl get gitrepositories -A
kubectl get kustomization -A -o=jsonpath='{.items[?(@.spec.sourceRef.name=="stackspout")].metadata.name}'
kubectl -n stackspout get helmreleases
kubectl -n stackspout get pods
```

But there are also ConfigMaps, Secrets, StatefulSets, PVCs, Helmrepos and all that stuff...
