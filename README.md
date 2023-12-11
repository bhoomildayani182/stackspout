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

### Guide: Creating OAuth Credentials for an external service
- add a line in `basic/install.sh` and run it to generate the secret (TODO: Update to new stackspin mechanism)
- append another OAuth2Client definition to `basic/overrides/oauth-clients.yaml`,
  adjusting `metadata.name` and `spec.secretName` as well as `spec.redirectUris`
- apply changes to the cluster 
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
basic/install.sh
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
