#!/usr/bin/env bash

echo "Creating / updating gitRepository custom-flux-example-basic in namespace flux-system"
flux create source git custom-flux-example \
  --url=https://open.greenhost.net/stackspin/custom-flux-example.git \
  --branch=main \
  --interval=1h

echo "Creating / updating kustomization custom-flux-example-basic in namespace flux-system"
flux create kustomization custom-flux-example-basic \
  --source=GitRepository/custom-flux-example \
  --path="./basic/clusters/production/" \
  --prune=true \
  --interval=1h
