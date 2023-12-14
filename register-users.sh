#!/bin/bash
source .env

SUB_DOMAINS=($SUB_DOMAIN_1 $SUB_DOMAIN_2)

for SUB_DOMAIN in "${SUB_DOMAINS[@]}"; do
    for USER in "${USERS[@]}"; do
        echo ${SUB_DOMAIN} $USER
        docker exec synapse-${SUB_DOMAIN} register_new_matrix_user -a -u $USER -p $USER -c /mx-conf/homeserver.yaml
    done
done
