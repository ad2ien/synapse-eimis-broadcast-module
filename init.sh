#!/bin/bash

source .env
SUB_DOMAINS=("litchi" "kiwi")

for SUB_DOMAIN in "${SUB_DOMAINS[@]}"; do
    docker run -it --rm \
        -v "./$SUB_DOMAIN/mx-data:/data" \
        -v "./$SUB_DOMAIN/mx-conf:/mx-conf" \
        -e SYNAPSE_SERVER_NAME=$SUB_DOMAIN.${DOMAIN} \
        -e SYNAPSE_CONFIG_PATH=/mx-conf/homeserver.yaml \
        -e SYNAPSE_REPORT_STATS=no \
        matrixdotorg/synapse:v1.83.0 generate

    sed -i -e 's/{{ DOMAIN }}/$DOMAIN/g' ./$SUB_DOMAIN/element-config.json
    
    echo "
serve_server_wellknown: true
modules:
- module: broadcast_module.EimisBroadcast
    config:
        url1: ${SUB_DOMAINS[0]}.$DOMAIN
        url2: ${SUB_DOMAINS[1]}.$DOMAIN
" >> ./$SUB_DOMAIN/mx-conf/homeserver.yaml

done
