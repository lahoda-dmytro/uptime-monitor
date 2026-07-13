# architecture overview

this project is a self-hosted uptime monitoring system built with a modular architecture and packaged using containerization. the environment is designed for both local development and direct deployment to a cloud vps.

## core components

the application stack consists of three docker containers connected through a dedicated bridge network:

* **nginx reverse proxy** – receives all incoming http requests on port `8080` during local development or ports `80` and `443` in production. it routes requests to the application, forwards the original client ip address through the appropriate headers, and prevents direct public access to the application container.

* **fastapi application** – the core python service that exposes rest api endpoints for managing monitored websites and runs an asynchronous background scheduler. the scheduler periodically retrieves active websites from the database and performs concurrent availability checks using `httpx`.

* **postgresql database** – the persistent data store containing the database schema for monitored websites and their check history. database data is stored in a docker named volume, allowing it to persist independently of the container lifecycle.

## network and data flow

all containers communicate within an isolated docker bridge network. the fastapi application connects to the database using the postgresql service name as the host, eliminating the need for hardcoded ip addresses.

the following diagram illustrates the request flow and the background monitoring process:

```text
[ client ] ---> ( port 8080 ) ---> [ nginx container ]
                                         |
                                         v
                                  ( port 8000 )
                                         |
                                         v
                                  [ fastapi app ] <---> [ postgresql ]
                                         ^
                                         |
                               [ background pinger ]
                                         |
                                         v
                                  [ target sites ]
```

during each monitoring cycle, the background scheduler sends concurrent asynchronous requests to all active target websites. the response time, http status code, and any encountered errors are recorded in the database, providing a complete history of website availability and performance.