#!/usr/bin/env bash

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Recreate and seed the database for each service
for SERVICE in ${ROOT_DIR}/services/*
do
    echo "Recreating database: $(basename ${SERVICE})"
    PODS=$(kubectl get pods --all-namespaces | grep $(basename ${SERVICE})'-' | grep -v 'db-' | awk '{print $2}')

    # https://stackoverflow.com/a/24628676
    SAVEIFS=$IFS
    IFS=$' '
    PODS=($PODS)
    IFS=$SAVEIFS

    for POD in $PODS; do
        kubectl exec -i $POD python manage.py recreate_db
        kubectl exec -i $POD python manage.py seed_db
    done

done