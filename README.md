# WHOI HABhub Data Portal

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Harmful Algal Bloom data API and map project. Our current version for Public Beta is now live! https://habhub.whoi.edu/

The "HABhub" data portal is being developed as a data access and visualization portal for the New England Harmful Algal Bloom Observing Network ([neHABON](https://northeasthab.whoi.edu/bloom-monitoring/habon-ne/)).

There are two separate applications that comprise the HABhub:
- a backend data server that provides a REST API. Built using the Django Python framework. You can find this app in the `habhub-dataserver` directory.
- a frontend client to visualize the data with an interactive map and charts. Built with the React JS framework. Located in the `habhub-react-frontend` directory.

These applications can run together on a shared machine as a single service or be set up independently of each other. The frontend client only needs to be configured with the base URL of the backend data server to access its API.

## Local Deployment with Docker

This project is configured to be deployed both locally and in production using Docker and Docker Compose. The default local deployment uses Docker Compose to run both applications in a single network from one `local.yml` compose file. 

Steps for default Local Deployment:

1. Docker and Docker Compose installed: [instructions](https://docs.docker.com/compose/install)
2. Clone repo to your local computer:  `git clone https://github.com/WHOIGit/whoi-hab-hub.git`
3. Create local `.env `files for both Django data server and React frontend client. Continued below...

**Step 3 details**

HABhub uses environmental variables for configs such as API links, API tokens, and secrets like database usernames/passwords.
These variable should NOT be kept in version control. 

**For the Django Data Server**

The `habhub-dataserver` directory contains the Django backend application. This directory also includes a ``.envs.example`` directory that you can use as
a template to create your own ``.envs`` directory and files. HABhub requires this ".envs" directory to be in the Django application root level directory. (ex. environmental variables file path: `habhub-dataserver/.envs/.production/.django`)

Final directory structure:

```
habhub-dataserver
-- .envs/
    -- .production/
      -- .django 
      -- .postgres
    -- .local/
      -- .django
      -- .postgres
```
**For the React Frontend Client**

The `habhub-react-frontend` directory contains the React frontend application. Create a new default `.env` file in this directory using the provided `.env.example` file as a template. You can also use the example `.env.development` and `.env.production` files to set different values for environmental variables depending on the environment. Any variable named in one of these environment specific files will be used instead of the default value in the regular `.env` file.

The required environmental variables are:
- REACT_APP_API_URL
- REACT_APP_MAPBOX_TOKEN

The REACT_APP_API_URL is the base URL of the HABhub data server you want to use. In the default local set up, this is http://localhost:8000/

The REACT_APP_MAPBOX_TOKEN is the API token for Mapbox access. To get a Mapbox GL JS token, create an account [here](https://account.mapbox.com/auth/signup/)

**Step 4**

Open your terminal and `cd` to the root level of the `whoi-hab-hub` directory. Run the following Docker Compose commands:
```
docker-compose -f local.yml build
docker-compose -f local.yml up
```
For the Django app, you need to run the initial DB migrations. Open up a second terminal and run:

```
docker-compose -f local.yml run --rm django python manage.py migrate
```
Then create the initial superuser, run:

```
docker-compose -f local.yml run --rm django python manage.py createsuperuser
```

The frontend map application will now be available at: http://localhost:3000/

The backend data server will be available at: http://localhost:8000/