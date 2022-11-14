#!/usr/bin/env bash

kubectl get namespace stackspout 2>/dev/null || kubectl create namespace stackspout

echo "Creating / Updating gitRepository stackspout"
flux create source git stackspout \
  --url=https://open.greenhost.net/xeruf/stackspout.git \
  --branch=main \
  --interval=5m

echo "Creating / Updating kustomization stackspout"
flux create kustomization stackspout \
  --source=GitRepository/stackspout \
  --path="./basic/infrastructure/kustomizations/" \
  --prune=true \
  --interval=5m

python $(dirname "$0")/../generate_secrets.py vikunja
python $(dirname "$0")/../generate_secrets.py vikunja-test
python $(dirname "$0")/../generate_secrets.py gitea
python $(dirname "$0")/../generate_secrets.py invoiceninja
#python $(dirname "$0")/../generate_secrets.py suitecrm
#python $(dirname "$0")/../generate_secrets.py kimai
python $(dirname "$0")/../generate_secrets.py wikijs
python $(dirname "$0")/../generate_secrets.py nextcloud-home
