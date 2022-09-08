# Server configs to run OnlyOne App

All this instructions are valid for an Ubuntu 20 installation.

## Prerequities

- You need first to install `nginx`, `certbot`, `docker` and `docker-compose`.

For nginx, execute simply these command in the terminal:
```bash
sudo apt-get update && apt-get upgrade
sudo apt-get install nginx
```

- Install docker by [following this instructions](https://docs.docker.com/engine/install/ubuntu/) and certbot by following [these](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)
## Python packages
Then install the Flask and Gunicorn with pip. Gunicorn is usefull to run the Flask server.
```bash
pip3 install Flask
pip3 install gunicorn
```
- Informations about [Flask](https://flask.palletsprojects.com/en/2.2.x/)
- Infromations about [Gunicorn](https://gunicorn.org/)


## Env variables
These variables are needed by the Flask script. The secret is a private symetric key. You must generate it with a cryptographically secure random number generator. The same key is to be registered on GiHub in the webhook settings.
```bash
export PROJECT_WEBHOOK_KEY=<secret>
export PROJECT_PARENT_DIR=/home/ubuntu
export PROJECT_NAME=OnlyOne
export PROJECT_URL=https://github.com/OneSock-inc/OnlyOne.git
export PROJECT_INFRA_DIR=OnlyOneInfra
```
## Domain name
To run the OnlyOne application, you need a domain name. Nginx will use it to redirect requests to the correct docker container. To enable https, use `certbot`.

## Config files

First go to home directory on the remote server and clone this repo. Then copy the config files in the right directory.  
WARNING: the nginx config file is a template. replace `<domain_name_here>` with valid FQDN.

```bash
cp ~/$PROJECT_INFRA_DIR/nginx/nginx-onlyone.conf /etc/nginx/sites-available/default

cp ~/$PROJECT_INFRA_DIR/gunicorn_service/gunicorn.service /etc/systemd/system/gunicorn.service

cp ~/$PROJECT_INFRA_DIR/gunicorn_service/gunicorn.socket /etc/systemd/system/gunicorn.socket
```

## Load services
```
sudo systemctl load gunicorn.service
sudo systemctl reload nginx
```
