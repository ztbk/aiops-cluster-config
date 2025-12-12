#!/bin/bash
set -x
PATH=${PWD}/bin/:$PATH

# check if parameter exists
if [ $# -lt 1 ]; then
    echo "No overlay specified, please specify an overlay from tenants/overlays"
    exit 1
fi

# check if parameter is valid
if [ ! -d tenants/overlays/$1 ]; then
  echo "Error. Overlay directory not found. Please specify a valid overlay name"
  exit 1
fi

OVERLAY=$1
echo "Configuring cluster ${OVERLAY}"

# apply resources
kustomize build tenants/overlays/${OVERLAY} --enable-helm | oc apply -n openshift-gitops -f -
