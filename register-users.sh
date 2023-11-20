#!/bin/bash
# set +eo
source .env

SUB_DOMAINS=("litchi" "kiwi")

for SUB_DOMAIN in "${SUB_DOMAINS[@]}"; do
    for USER in "${USERS[@]}"; do
        echo ${SUB_DOMAIN} $USER
        docker exec broadcast_poc_synapse-${SUB_DOMAIN}_1 register_new_matrix_user -a -u $USER -p $USER -c /mx-conf/homeserver.yaml
    done
done
