# Example repository for customizing a Stackspin cluster

Example boilerplate for a custom [flux](https://fluxcd.io/) repository
which can be added to a [Stackspin](https://stackspin.net) cluster.
The main use-case is to add additional applications
which are not integrated into Stackspin (yet).

For a more advanced example
see the [flux2-kustomize-helm-example](https://github.com/fluxcd/flux2-kustomize-helm-example)
repository.
This repo's directory structure is similar to the `flux2-kustomize-helm-example`
one.

## Basic configuration

We'll start with a very basic configuration:

* It uses a public git repo
* No secrets are included
* No forking/modifications needed, install as it is

Apply it to your cluster:

```sh
basic/install.sh
```

List the resource created by this flux repo:

```sh
kubectl -n example-basic get gitrepositories
kubectl -n example-basic get kustomizations
kubectl -n example-basic get helmreleases
kubectl -n example-basic get pods
```

Show output of the single app applied, [podinfo](https://github.com/stefanprodan/podinfo)

```sh
curl --resolve podinfo.local:80:CLUSTER_IPV4_ADDRESS http://podinfo.local
```

## What's next ?

There are two ways of using a custom flux repo to host your custom config/apps
on a Stackspin cluster.

### A) Manage secrets manually

This approach is easier to start with,
because you don't need to configure your cluster to handle encrypted secrets
and access to a private git repository.

* Fork this repository into a public git repo, cloneable via `https://`

### Everything in version control, including secrets

* Fork this repository into a private git repo, cloneable via `ssh://`
* [Configure flux to use ssh instead of https for cloning](https://fluxcd.io/docs/components/source/gitrepositories/#ssh-authentication)
* You shouln't rely solely on transport encryption for your git repository
  but rather end-to-end encrypt your secrets.
  Different methods are available for flux:
  * [Sops](https://fluxcd.io/docs/guides/mozilla-sops/)
    [Sops section in flux2-kustomize-helm-example](https://github.com/fluxcd/flux2-kustomize-helm-example#encrypt-kubernetes-secrets)
  * [Sealed Secrets](https://fluxcd.io/docs/guides/sealed-secrets/)
