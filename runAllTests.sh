#!/usr/bin/env bash
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
for SERVICE in ${ROOT_DIR}/services/*
do
    POD=$(kubectl get pods --all-namespaces | grep $(basename ${SERVICE})'-' | grep -v 'db-' | awk '{print $2}')
    kubectl exec -i $POD python manage.py test
done