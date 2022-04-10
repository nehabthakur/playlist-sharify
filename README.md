# playlist-sharify

## Description
This is a playlist maker and organiser for music, using the API from Last.FM. We wanted to be able to create our own cloud service that performs similar actions to existing music platforms. Understanding the uses and advantages of having the freedom to create playlists to produce a particular desired musical atmosphere, and our project will deliver this.

Playlists are usually tied down to the platform that you're using, but this application will overcome that problem to provide users access to cross-platform playlists.

## Methods
- PUT on `/sign-up`:   
  - This requires `Content-Type -> application/json` in the header.   
  - `username`, `password`, `name` should be part of the body.  
  - `username` should be between 7 and 29 characters. It shouldn't be empty, should have atleast one uppercase, lowercase, number and underscore symbol.
  - `password` should be between 8 and 32 characters. It shouldn't be empty, should have atleast one uppercase, lowercase, number and symbol.
  - `name` shouldn't be empty.  
  

- GET on `/playlist`:  
  - This requires `Content-Type -> application/json` and basic auth `username` and `password` in the header.   
  - `name` should be part of the body json, shouldn't be empty and also shouldn't already be created.  
 

- PUT on `/playlist`:  
  - This requires `Content-Type -> application/json` and basic auth `username` and `password` in the header.   
  - `name` should be part of the body json, shouldn't be empty and also should already be created.


- PATCH on `/playlist`:  
  - This requires `Content-Type -> application/json` and basic auth `username` and `password` in the header.   
  - `name` should be part of the body json, shouldn't be empty and also should already be created.
  - `track` should be part of the body json, shouldn't be empty, should be valid.
  - `artist` should be part of the body json, shouldn't be empty, should be valid.
  - `op_type` should be part of the body json, shouldn't be empty, should be valid(`ADD` or `DELETE`).


- DELETE on `/playlist`:  
  - This requires `Content-Type -> application/json` and basic auth `username` and `password` in the header.   
  - `name` should be part of the body, shouldn't be empty and also should already be created.


- GET on `/song`:  
  - This requires `Content-Type -> application/json` and basic auth `username` and `password` in the header.
  - `track` should be part of the body json, shouldn't be empty, should be valid.
  - `artist` should be part of the body json, shouldn't be empty, should be valid.
  

## Architecture

We use the below tools/technologies to build and run our application:
- **Python** - [Python 3.10](https://docs.python.org/3/whatsnew/3.10.html) is used for this project
- **Flask** - [Flask](https://flask.palletsprojects.com/en/2.1.x/) is a micro-web framework written in python to simplify creation of RESTFUL and HTTP applications
- **GEvent** - [GEvent](http://www.gevent.org/) is a coroutine based python networking library that provides support for concurrent, api calls
- **Kubernetes** - [Kubernetes](https://kubernetes.io/) is an open-source orchestration framework used for automating deployment, scaling and management of containerized applications
- **Docker** - [Docker](https://www.docker.com/) is a PAAS product that offers OS-level virtualization through containers
- **MongoDB** - [MongoDB](https://www.mongodb.com/) is a document based no SQL database
- **Google Kubernetes Engine** - [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine) is an orchestration system for docker containers
- **Artifact Registry (GCP)** - [Artifact Registry](https://cloud.google.com/artifact-registry) is a registry to store built docker images
- **Secret Manager (GCP)** - [Secret Manager (GCP)](https://cloud.google.com/secret-manager) is to store secrets that can be accessed securely from the application
- **Cloud Build (GCP)** - [Cloud Build (GCP)](https://cloud.google.com/build) is a serverless ci/cd platform which can be used to build and deploy containers in GKE

This application uses [GKE Autopilot](https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview) which removes the overhead of provisioning nodes for the kubernetes cluster.
It automatically manages, optimizes the nodes, node pools in the kubernetes clusters for both development and production workloads. This reduces a lot of DevOps workload for maintaining the Kubernetes cluster.
The customers only pay for the cpu, memory used.

This application uses [MongoDB](https://www.mongodb.com/) as a database storage layer. Since, most of the data is written and queried in a document-based format, MongoDB is chosen. 
MongoDB is deployed as a SAAS tool in GCP to make sure the rest api has very low latency.

This application uses [Secret Manager (GCP)](https://cloud.google.com/secret-manager) to store secrets such as api keys for song data provider last-fm and mongodb credentials. 
This provides a secure way to access the keys during runtime and helps avoid writing keys in the code.

This application uses [Cloud Build (GCP)](https://cloud.google.com/build) to automatically build and deploy the code into GKE autopilot cluster whenever new commits are pushed to the [GitHub repo](https://github.com/nehabthakur/playlist-sharify) main branch.
We have adopted the [GitOps](https://www.weave.works/technologies/gitops/) methodology of CI/CD to automatically deploy changes once they're developed and tested.
We have created a trigger in Cloud Build that continuously polls the GitHub repo's main branch and looks for [cloudbuild file](cloudbuild.yaml) and runs the following steps. 
Builds the image and pushes it to [Artifact Registry (GCP)](https://cloud.google.com/artifact-registry). 
It will then deploy the kubernetes config files defined in [tools/k8s/gke](tools/k8s/gke) to GKE Autopilot cluster automatically.

![Architecture diagram](static/architecture.png)

## Application Flow

![Application Flow](static/flow.png)

## Code

- All the external python libraries are defined in [requirements.txt](requirements.txt)
- The starting point of code is [main.py](main.py) which loads the environment variables and starts the rest api application server 
- [app.py](src/app.py) consists of all the routing, logging information for the rest api
- [src.models](src/models) package consists of all the application logic when the APIs is called
- [src.utils](src/utils) package consists of utility functions to support calling the external api and mongodb
- [cloudbuild.yaml](cloudbuild.yaml) file consists of the ci/cd steps defined as code
- [tools/docker](tools/docker) directory consists of the Dockerfile which packages the application as a container image
- [tools/k8s](tools/k8s) directory consists of yaml files to run the built container image in kubernetes

## Instructions

### Pre-requisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Python](https://www.python.org/downloads/)
- [Kubernetes](https://kubernetes.io/releases/download/)
- [Postman](https://www.postman.com/downloads/)

### Additional Pre-requisites for running on cloud
- [Google cloud](https://cloud.google.com/) - Create a Google cloud account, setup billing
- [MongoDB cloud](https://www.mongodb.com/cloud) - Create a mongodb account and launch an instance in google cloud(free or standard)
- [Last.fm](https://www.last.fm/api/account/create) - Create a last.fm api account and store the api_creds

### Local
This will run the application directly on the personal machine on port 5000. Below are the steps:

#### Steps
1. Store the api creds in a json format as an env variable with name `API_CREDS` and format `{"api_key": "<add api key here>"}`
2. Store the mongodb creds in a json format as an env variable with name `MONGO_CREDS` and format `{"username": "<update the value here>","password":"<update the value here>","cluster_id":"<update the value here>"}`
3. Run `python main.py` to run the application.
4. Application can be accessed using this [localhost:5000](http://localhost:5000)

### Local Kubernetes
This will run the application using Kubernetes on the personal machine on port 5000. Below are the steps:

#### Steps
1. Update the `API_CREDS` in [K8s config](tools/k8s/local/01-deployment.yaml) in a json format `{"api_key": "<add api key here>"}`
2. Update the `MONGO_CREDS` in [K8s config](tools/k8s/local/01-deployment.yaml) in a json format `{"username": "<update the value here>","password":"<update the value here>","cluster_id":"<update the value here>"}`
3. Build the docker image using `docker build -t playlist-sharify:latest -f tools/docker/Dockerfile .`
4. Deploy image using `kubectl apply -f .\tools\k8s\local\`

### GKE
This will run the application using GKE autopilot on google cloud. Below are the steps:

#### Steps
1. Create an [GKE Autopilot](https://console.cloud.google.com/kubernetes/list/overview) Cluster
2. Create a secret in [Secret Manager](https://console.cloud.google.com/security/secret-manager) with name `last_fm_credentials` in a json format `{"api_key": "<add api key here>"}`
3. Create a secret in [Secret Manager](https://console.cloud.google.com/security/secret-manager) with name `mongodb_playlist_sharify_credentials` in a json format `{"username": "<update the value here>","password":"<update the value here>","cluster_id":"<update the value here>"}`
4. Create a trigger in [Cloud Build](https://console.cloud.google.com/cloud-build/triggers) that triggers a build when a new commit is pushed to the main branch in GitHub
5. Trigger should have the following properties:
   1. Event should be `Push to a branch`
   2. Connect the GitHub Repo and set branch to `^main$`
   3. Configuration should use Cloud Build Configuration file
   4. Location should be Repository and set the configuration file to be `cloudbuild.yaml`
   5. Set the following substitution variables
      1. `_API_SECRET` -> `last_fm_credentials`
      2. `_API_SECRET_VERSION` -> `<Set the API Secret Version>`
      3. `_GKE_CLUSTER_ID` -> `<Set the GKE cluster id>`
      4. `_IMAGE` -> `playlist-sharify-api`
      5. `_LOCATION` -> `<Set the location as per your preference>`
      6. `_MONGO_DB_SECRET` -> `mongodb_playlist_sharify_credentials`
      7. `_MONGO_DB_SECRET_VERSION` -> `<Set the MongoDB Secret Version>`
      8. `_REPOSITORY` -> `<Set the Repository Name>`
6. Enable Access to `GKE` and `Secret Manager` in [Cloud Build](https://console.cloud.google.com/cloud-build/settings/service-account) settings
7. Deploy and start the service either by pushing a new commit or running the cloud build trigger [manually](https://console.cloud.google.com/cloud-build/triggers)
8. Access the app by opening the endpoint in `playlist-sharify-service` in [GKE Services Page](https://console.cloud.google.com/kubernetes/discovery)
