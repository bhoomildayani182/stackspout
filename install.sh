#!/usr/bin/env bash

kubectl get namespace stackspout 2>/dev/null || kubectl create namespace stackspout

echo "Creating / Updating gitRepository stackspout"
flux create source git stackspout \
  --url=https://forge.ftt.gmbh/polygon/stackspout.git \
  --branch=main \
  --interval=5m

echo "Creating / Updating kustomization stackspout"
flux create kustomization stackspout \
  --source=GitRepository/stackspout \
  --path="./infrastructure/kustomizations/" \
  --prune=true \
  --interval=5m

# Required for oversized truecharts repo
export GITEA_TOKEN=$(pass business/ftt/stackspout)
flux bootstrap gitea \
  --token-auth \
  --branch=main \
  --hostname=forge.ftt.gmbh \
  --owner=polygon \
  --repository=stackspout \
  --path=util/flux
