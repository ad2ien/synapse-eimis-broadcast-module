# Synapse broadcast module

> [!IMPORTANT]  
> 🚧 This repo hosts a POC and is not meant to be used

## Use case 📖

- a user is part of a private federation in which, for some reason, has several accounts on different homeserver
- there's a 3rd party service linking the user and its MXID
- the user wants all the conversations of all his/her MXIDs to be synchronized
- if a message is read (or sent) with a MXID it should be marked read for every MXID

## Ideas 💡

## The Tchap way

- A users creates an account on any of the federation servers
- At login, Element (or other clients), calls a service to select the right server to connect to, depending on a 3PId [the code here](https://github.com/tchapgouv/tchap-web-v4/blob/22af08b728ebf4ba45b6baada551d3833e7facee/patches/login/matrix-react-sdk%2B3.92.0.patch#L50)
- In the interface the displayed name is preferred over the MXID

### Pros 👍

- Already implemented with Tchap
- Unique account with federated architecture

### Cons 👎

- If a server closes, accounts have to be migrated, users probably lose their messages
- Not obvious to implement for non-Element clients
- More complicated than [centralized architecture](https://github.com/eimis-ans/eimis-synapse/wiki/Architectures-et-impl%C3%A9mentation-par-les-%C3%A9diteurs#sc%C3%A9nario-architecture-centralis%C3%A9e-mxid-unique) with the constraints of the federated one

## With some new EIMIS modules

These requirements could be met with a Synapse module :

- when a user is invited to or creates a room, all its MXID are invited
- when a message is read, it should be marked as read for all the MXID

## Limitations 🚧

- The receipts part should not be modified like this, but it's just a POC 🤷🏻

## Directory

For this POC a stubb directory has been created using [grist](https://www.getgrist.com/). For CORS purpose, a [synapse module](./eimis_directory_module/) acts as a proxy.  

## Run the POC 🚜

### Prerequisites

- docker / docker compose installed
- traefik and domain name configured

### Start the stack

- fill the .env file

  ```.env
  TRAEFIK_NETWORK=
  DOMAIN=
  USER=("admin_matrix" "alice" "bob")
  SUB_DOMAIN_1=kiwi
  SUB_DOMAIN_2=litchi
  DIRECTORY_URL=https://something-that-returns-an-array-of-mxid?mxid=
  ```

__DIRECTORY_URL :__ an url that, concatenated with a MXID, should return a json array of linked mxid.

- start the stack
  
  ```bash
  chmod +x *.sh  
  ./init.sh
  docker-compose up -d
  ```

- register users (configure in.env) in both servers (password=username, all admin : YOLO!)

  ```bash
  ./register-users.sh
  ```

- if you want to reset the stack (erase database)

  ```bash
  ./reset-stack.sh
  ```

docker-compose logs etc... and go to your domain, login, create room, invite user and try it out!
