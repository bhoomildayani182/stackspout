#!/bin/sh -e
# Generates kubernetes kustomizations
if test $# -gt 0
then dir=$1
	{ echo 'apiVersion: kustomize.config.k8s.io/v1
kind: Kustomization
resources:'
	find $dir -maxdepth 1 -type f -name "*.yaml" -not -name "kustomization.yaml" -printf "  - %f\n"; } | tee $dir/kustomization.yaml
else
	find -mindepth 1 -maxdepth 1 -type d | while read dir
		do echo "$dir"
			$0 "$dir"
		done
fi
