.PHONY: check-requirments build
check-requirments:
	@which oc || (echo "oc is not installed"; exit 1)
	@which kustomize || (echo "kustomize is not installed"; exit 1)

build:
	kustomize build bootstrap/overlays/${OVERLAY} --enable-helm | oc apply -n openshift-gitops -f -

build-dry-run:
	kustomize build bootstrap/overlays/${OVERLAY}  --enable-helm
