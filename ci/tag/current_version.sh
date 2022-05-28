#!/usr/bin/env bash

set -euo pipefail

current_version=$(git tag -l --sort=v:refname | tail -n1)
current_version_number=$(echo ${current_version} | sed "s/^v//")
if [ -z "${current_version_number}" ] ; then
	current_version_number="0.0.0"
fi
current_version="v${current_version_number}"

echo ${current_version}
