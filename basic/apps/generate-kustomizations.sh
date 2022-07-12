#!/bin/sh -e
# Generates kubernetes kustomizations
find -mindepth 1 -maxdepth 1 -type d | while read dir;
do  echo "$dir"
	{ echo 'apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:'
	find $dir -type f -not -name "*.bak" -printf "  - %f\n"; } | tee $dir/kustomization.yaml
done
