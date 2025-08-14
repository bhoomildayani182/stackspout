# Stackspin Outwards – Stackspout 🚀

This repository extends [Stackspin](https://open.greenhost.net/stackspin/stackspin)
with extra applications and overrides focused on business use.
Once stabilized, the aim is to contribute as much upstream as possible.

Stackspout is used in day-to-day business
with a double-digit user number,
so all experiments happen carefully.
Still, it is an experimental offering ⚠

---

## Customizations ⚙

### Overrides 🔧

* Adds many Nextcloud extensions and some configuration
* Allow iFraming of applications into Nextcloud

---

## New Applications ➕

Following are the applications Stackspout adds beyond Stackspin.
Unlike Stackspin, there is currently no mechanism to add those individually —
they come in one package with the repository.

Below list is formatted as:

> subdomain: Service (helmrepo, if not by the application authors themselves)

---

### Stackspin included Tools 🧰

* `dashboard`: Toolübersicht von Stackspin
* `files`: Nextcloud – Tools Hub, Dokumentation, Filesharing, Kalender, Kontakte 📁
* `chat`: Zulip – Kommunikation und Arbeitsdokumentation 💬
* `note`: Hedgedoc – Lebende, kollaborative Dokumente 📝

---

### Stable including OpenID Connect Single Sign-On 🔐

* `forge`: Forgejo – Code Repositories
* `do`: Vikunja – Projektmanagement
* `status`: Gatus (minicloudlabs) – Status-Überwachung Monitor

---

### No Single Sign-On 🔓

#### LDAP Support
* `ninja`: InvoiceNinja – Rechnungsstellung, Angebote, ggf. Zeiterfassung 💰 (requires 30$ per year for whitelabeling)
* `support`: Zammad – Kundensupport & Login-Codes 🧾 (updates pending)

#### Paid Plan required for SSO
* `flow`: n8n (8gears) – Automatisierungen 🔁
* `meet`: cal.com (pyrrha) – Terminvereinbarungen 📅 ([Enterprise License for SSO](https://cal.com/docs/self-hosting/sso-setup))
* `board`: openproject  (https://www.openproject.org/docs/installation-and-operations/installation/helm-chart/) – Projektplanung 📋

---

### Coming Soon 🔜

* `sign`: [Docuseal](https://github.com/zekker6/helm-charts/tree/main/charts/apps/docuseal) / Documenso– Signaturen 🔏
* `design`: Penpot – Design-Tool 🎨
* `stirling`: PDF Manipulation Hub / Toolbox

---

### Planned 📌

* `sprint`: Taiga (nemonik) – Agile Boards 🏃
* `video`: Peertube ([LecygneNoir](https://git.lecygnenoir.info/LecygneN
oir/peertube-helm)) – Dezentrales Video-Hosting

---

### Ideas 💡

* `wiki/know`: Wiki – evtl. Wiki.js, preferred Integration with Nextcloud + Markdown/Orgdown?
* `call`: Jitsi Meet / OpenTalk / Element Call
* `link`: URL Shortener 🔗
* `connect`: Bonfire – Social & Community Tools

---

### Stale 💤

* `people`: SuiteCRM (bitnami repo)
* `time`: Kimai (robjuz repo)

---

### Configuration Tasks ☐

- Nextcloud too slow - add Redis?
- Preconfigure user settings in Nextcloud, Vikunja and more

---

## Setup Instructions 🧭

> **Warning:** This toolset is in active experimentation!
> Data loss can happen!

First [install Stackspin](https://docs.stackspin.net/en/latest/installation/install_stackspin.html).
Then apply the configuration to your cluster:

```sh
./install.sh
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

## Tools and Guides

Useful tools for administration:
- my `stack` CLI helper, currently part of my dotfiles:
  https://forge.ftt.gmbh/janek/dotfiles/src/branch/main/.config/shell/server#L21
- stackspin docs:
  https://docs.stackspin.net/en/v2/system_administration/customizing.html
  
### Adding a new app

Also see https://open.greenhost.net/stackspin/stackspin/-/blob/main/.gitlab/issue_templates/new_app.md?ref_type=heads#source-helmrepository--gitrepository

A template for most of these steps can be generated using https://forge.ftt.gmbh/janek/dotfiles/src/branch/main/.local/bin/scripts/stack-template

- create the HelmRepository in [`infrastructure/sources`](./infrastructure/sources)
- create a folder with app configuration files under [`apps`](./apps)
- add a kustomization for the app into [`apps`](./apps) and add it to [`apps/kustomization.yaml`](./apps/kustomization.yaml) when the app is ready

### Creating OAuth Credentials for an External Service
- push an OAuth2Client definition like for the apps,
  adjusting `metadata.name` and `spec.secretName` as well as `spec.redirectUris`
- obtain the generated `client_secret` for your application from kubernetes:

      kubectl get secret -n flux-system stackspin-APP-oauth-variables --template '{{.data.client_secret}}' | base64 -d

  with client_id:

      kubectl get secret -n flux-system stackspin-APP-oauth-variables --template '{{.data.client_id}}{{"\n"}}{{.data.client_secret}}{{"\n"}}' | while read in; do echo $in | base64 -d; echo; done


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

![Flux Diagram](util/stackspout.png)

See also https://about.ftt.gmbh/projects/polygon.html#state-of-stackspout-2022
