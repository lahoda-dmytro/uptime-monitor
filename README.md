# uptime monitor homelab

this repository contains a self-hosted uptime monitoring system that periodically checks a list of websites and stores their availability status in a database. it is designed as a hands-on project for learning and practicing modern devops principles, including containerization, infrastructure as code, continuous integration and deployment, automation, and monitoring.

## architecture

the system consists of three main services running in docker containers:

- fastapi – the core application that exposes a rest api and runs a background scheduler responsible for periodically checking website availability.
- nginx – a reverse proxy that handles incoming requests and forwards them to the fastapi application.
- postgresql – the persistent database that stores the list of monitored websites and their historical status check results.

the infrastructure is provisioned using terraform to create an azure virtual machine, ansible is used to configure the operating system and docker environment, and github actions provides continuous integration and automated deployment pipelines.

## repository layout

* `app/` - fastapi application source code, project dependencies, and the application dockerfile.
* `compose/` - docker compose configuration for local development and production deployment.
* `nginx/` - nginx reverse proxy configuration files.
* `postgres/` - sql initialization scripts for database setup.
* `scripts/` - shell scripts for deployment, backups, health checks, and maintenance tasks.
* `terraform/` - terraform configuration files for provisioning azure infrastructure.
* `ansible/` - ansible playbooks and roles for server configuration.
* `.github/` - github actions workflows for ci/cd automation.
* `docs/` - project documentation, including architecture and deployment guides.