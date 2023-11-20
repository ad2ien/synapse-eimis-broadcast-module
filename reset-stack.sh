SUB_DOMAINS=("litchi" "kiwi")

docker-compose down

for SUB_DOMAIN in "${SUB_DOMAINS[@]}"; do
    sudo rm ./$SUB_DOMAIN/mx-data/homeserver.db
done

docker-compose up -d
docker-compose logs -f
