#!/usr/bin/env bash

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Recreate and seed the database for each service
for SERVICE in ${ROOT_DIR}/services/*
do
    echo "Recreating database: $(basename ${SERVICE})"
    POD=$(kubectl get pods --all-namespaces | grep $(basename ${SERVICE})'-' | grep -v 'db-' | awk '{print $2}')
    kubectl exec -i $POD python manage.py recreate_db
    kubectl exec -i $POD python manage.py seed_db
done