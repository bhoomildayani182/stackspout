#!/usr/bin/env bash

kubectl get namespace stackspout 2>/dev/null || kubectl create namespace stackspout

echo "Creating / updating gitRepository stackspout in namespace stackspout"
flux create source git stackspout \
  --namespace=stackspout \
  --url=https://open.greenhost.net/xeruf/stackspout.git \
  --branch=main \
  --interval=10m

echo "Creating / updating kustomization stackspout in namespace stackspout"
flux create kustomization stackspout \
  --namespace=stackspout \
  --source=GitRepository/stackspout \
  --path="./basic/clusters/production/" \
  --prune=true \
  --interval=10m

python ../../stackspin/install/generate_secrets.py vikunja
python ../../stackspin/install/generate_secrets.py gitea
