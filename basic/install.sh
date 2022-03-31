#!/usr/bin/env bash

echo "Creating / updating gitRepository stackspin-flux-example-basic in namespace example-basic"
flux create source git stackspin-flux-example \
  --namespace=example-basic \
  --url=https://open.greenhost.net/stackspin/stackspin-flux-example.git \
  --branch=main \
  --interval=1h

echo "Creating / updating kustomization stackspin-flux-example in namespace example-basic"
flux create kustomization stackspin-flux-example \
  --namespace=example-basic \
  --source=GitRepository/stackspin-flux-example \
  --path="./basic/clusters/production/" \
  --prune=true \
  --interval=1h
