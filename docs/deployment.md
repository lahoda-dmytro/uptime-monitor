# deployment guide

this guide explains how to provision a virtual machine in azure, configure it for docker compose, and set up automated deployments using github actions.

## vps setup

you will need a linux virtual machine (ubuntu server 22.04 lts is recommended) running in azure.

1. **provision the vm**: create the virtual machine using the azure portal or azure cli. make sure it is assigned a public ip address.
2. **configure networking (firewall)**: in the azure vm's network security group (nsg), create inbound security rules to allow:
   * port `22` (ssh) - for remote ssh access and deployment.
   * port `80` (http) - for incoming web traffic.
   * port `443` (https) - for secure web traffic.
3. **install docker**: connect to the virtual machine over ssh and install docker together with the docker compose plugin by running the standard installation commands:
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose-v2
   sudo usermod -aG docker $USER
   ```
   log out and sign in again for the group membership changes to take effect.

## directory and environment setup

create the application directory on the server where the project will be deployed:

```bash
sudo mkdir -p /var/www/uptime-monitor
sudo chown -R $USER:$USER /var/www/uptime-monitor
```

clone the repository into `/var/www/uptime-monitor` (or initialize a git repository and pull the `main` branch). inside the project directory, manually create the `.env` file. it should contain the production database credentials and application configuration:

```env
POSTGRES_DB=uptime_monitor
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_production_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
APP_PORT=8000
PING_INTERVAL_SECONDS=60
```

## configure github actions secrets

to allow github actions to securely connect to the server, configure the required repository secrets in github:

1. **generate ssh key**: on your local machine or on the server, generate a new ssh key pair:
   ```bash
   ssh-keygen -t ed25519 -C "deploy@uptime-monitor"
   ```
2. **add public key to server**: append the contents of the generated `.pub` key to `~/.ssh/authorized_keys` on the server.
3. **add secrets in github**: open your github repository and navigate to **settings → secrets and variables → actions → new repository secret**. add the following secrets:
   * `SERVER_IP` - the public ip address of your azure virtual machine.
   * `SERVER_USER` - the ssh username (for example, `azureuser` or `ubuntu`).
   * `SSH_PRIVATE_KEY` - the complete contents of the private key (`id_ed25519`).

## first deployment

once the repository secrets have been configured and the application directory has been initialized, every push or merged pull request into the `main` branch will automatically trigger the deployment pipeline.

github actions will connect to the server, execute `git pull`, rebuild the docker images, start the application containers, and run the health check to verify that the application has been deployed successfully.