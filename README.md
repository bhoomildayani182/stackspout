# custom-flux-example

Example boilerplate for a custom f[lux](https://fluxcd.io/) repository which can be added to a [Stackspin](https://stackspin.net) cluster.
The main use-case is to add additional applications which are not integrated into Stackspin (yet).

For a more advanced example repo see the [flux2-kustomize-helm-example](https://github.com/fluxcd/flux2-kustomize-helm-example) repo.
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
kubectl -n flux-system get gitrepositories
kubectl -n flux-system get kustomizations
kubectl -n example get helmreleases
```

Show output of the one and only app applied, [podinfo](https://github.com/stefanprodan/podinfo)

```sh
curl --resolve podinfo.local:80:CLUSTER_IPV4_ADDRESS http://podinfo.local
```

## What's next ?

* Fork this repo to a private git remote
* Configure flux to use ssh instead of https for cloning
* Add private ssh key for git pulling to flux
* Add public ssh key for git pulling to your git remote
* [Encrypt your secrets using sops](https://github.com/fluxcd/flux2-kustomize-helm-example#encrypt-kubernetes-secrets)
