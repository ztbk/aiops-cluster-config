#!/bin/bash
set -x
PATH=${PWD}/bin/:$PATH

# check if parameter exists
if [ $# -lt 1 ]; then
    echo "No overlay specified, please specify an overlay from bootstrap/overlays"
    exit 1
fi

# check if parameter is valid
if [ ! -d bootstrap/overlays/$1 ]; then
  echo "Error. Overlay directory not found. Please specify a valid overlay name"
  exit 1
fi

OVERLAY=$1
echo "Configuring cluster ${OVERLAY}"

# install openshift-gitops operator resources
oc get argocd -n openshift-gitops openshift-gitops &>/dev/null
if [[ $? -eq 1 ]]; then
  echo "ArgoCD instance not detected. Installing operator."

  # cleanup existing installplans
  oc -n openshift-gitops-operator delete installplan --all

  # create resources
  cat <<EOF | oc apply -f -
---
apiVersion: v1
kind: Namespace
metadata:
  labels:
    kubernetes.io/metadata.name: openshift-gitops-operator
  name: openshift-gitops-operator
---
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: openshift-gitops-operator-2shhc
  namespace: openshift-gitops-operator
spec:
  upgradeStrategy: Default
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  labels:
    operators.coreos.com/openshift-gitops-operator.openshift-gitops-operator: ""
  name: openshift-gitops-operator
  namespace: openshift-gitops-operator
spec:
  channel: latest
  installPlanApproval: Manual
  name: openshift-gitops-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
  startingCSV: openshift-gitops-operator.v1.15.0
EOF

  # approve new installplan
  sleep 60
  installPlan=$(oc -n openshift-gitops-operator get subscriptions.operators.coreos.com -o jsonpath='{.items[0].status.installPlanRef.name}')
  oc -n openshift-gitops-operator patch installplan "${installPlan}" --type=json -p='[{"op":"replace","path": "/spec/approved", "value": true}]'

  # wait until argocd instance is available
  status=$(oc -n openshift-gitops get argocd openshift-gitops -o jsonpath='{ .status.phase }')
  while [[ "${status}" != "Available" ]]; do
    sleep 5;
    status=$(oc -n openshift-gitops get argocd openshift-gitops -o jsonpath='{ .status.phase }')
  done

  # annotate it to enable SSA
  oc -n openshift-gitops annotate --overwrite argocd/openshift-gitops argocd.argoproj.io/sync-options=ServerSideApply=true
fi

# apply resources
kustomize build bootstrap/overlays/${OVERLAY} --enable-helm | oc apply -n openshift-gitops -f -
