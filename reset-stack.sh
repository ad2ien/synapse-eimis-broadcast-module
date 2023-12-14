#!/bin/bash
source .env

SUB_DOMAINS=($SUB_DOMAIN_1 $SUB_DOMAIN_2)

docker-compose down

for SUB_DOMAIN in "${SUB_DOMAINS[@]}"; do
    sudo rm ./$SUB_DOMAIN/mx-data/homeserver.db
done

docker-compose up -d
docker-compose logs -f
