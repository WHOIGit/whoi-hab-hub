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

### Steps for initial Local Deployment:

1. Docker and Docker Compose installed: [instructions](https://docs.docker.com/compose/install)
2. Clone repo to your local computer: `git clone https://github.com/WHOIGit/whoi-hab-hub.git`
3. Create local `.env` files for both Django data server and React frontend client. Continued below...

**Step 3 details**

HABhub uses environmental variables for configs such as API links, API tokens, and secrets like database usernames/passwords.
These variable should NOT be kept in version control.

**For the Django Data Server**

The `habhub-dataserver` directory contains the Django backend application. This directory also includes a `.envs.example` directory that you can use as
a template to create your own `.envs` directory and files. HABhub requires this ".envs" directory to be in the Django application root level directory. (ex. environmental variables file path: `habhub-dataserver/.envs/.local/.django`)

Final directory structure:

```
habhub-dataserver
-- .envs/
    -- .local/
      -- .django
      -- .postgres
    -- .production/
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

You can also change the default initial map configuration settings for both the latitude/longitude and zoom:

- REACT_APP_MAP_LATITUDE
- REACT_APP_MAP_LONGITUDE
- REACT_APP_MAP_ZOOM

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

To access the Django admin system, login with your new superuser credentials at: http://localhost:8000/admin

### Initial HABHub Data Server Configuration

Login to the Django admin panel to access the HABHub Data Server settings.

There are two `Core` data models that need to be configured to work with the HABHub React Frontend Client and the IFCB Dashboard.

**Data Layers**

These are the different data layers that are available to display on the frontend HABHub map. By default, all of them are active. To remove a data layer from the frontend map, edit it and simply uncheck the "Is Active" checkbox.

http://localhost:8000/admin/core/datalayer/

**Target Species**

This is the list of HAB species that are available for both data ingestion from a IFCB Dashboard and to interact with in the frontend map.

http://localhost:8000/admin/core/targetspecies/

The default list is pre-configured with the six species of interest from the main https://habhub.whoi.edu/ site. To ingest IFCB data for a species from an IFCB Dashboard, you just need to make sure that the "species_id" field matches the text string that is used in the IFCB dashboard Autoclass files to identify the species. Ex. file: https://habon-ifcb.whoi.edu/harpswell/D20200221T223958_IFCB000_class_scores.csv

You can also choose the primary color for each species for display on the map. A color gradient using that color is automatically created when you change a species color

**IFCB Datasets Layer**

To configure this data layer, you need to first create some Dataset objects in the admin panel:

http://localhost:8000/admin/ifcb_datasets/dataset/

These Datasets should match with an existing Dataset in your IFCB Dashboard. The "Dashboard id name" field needs to be set to the unique ID from the IFCB Dashboard. This can be found in the IFCB Dashboard URL for the dataset, ex: https://habon-ifcb.whoi.edu/timeline?dataset=harpswell, or at the bottom of the "Basic Info" box in the Dashboard.

Once a Dataset is created in HABhub, data from the Target Species will begin to automatically be ingested on an hourly basis. No further configuration is necessary.

**Shellfish Toxicity Layer**

First create some geographic Station locations in the admin panel that are providing Shellfish Toxicity data. You can then import data from a CSV for each Station using the Datapoint importer:

http://localhost:8000/admin/stations/datapoint/import/

**Closures Layer**

This layer is very dependent on specific state government data and protocols. Example data is available for some New England states, but this layer requires custom set up for new states and is still under development.

### Steps to update Local Deployment:

To update your local version with the latest code changes from the `main` repo branch, take the following steps:

1. `cd` to the project root directory
2. `git pull` to get the latest version
3. `docker-compose -f local.yml down`
4. `docker-compose -f local.yml build`
5. `docker-compose -f local.yml up --renew-anon-volumes` (the `--renew-anon-volumes` option makes sure that your local `node_modules` volume is updated with any package changes.)
