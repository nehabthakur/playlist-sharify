# playlist-sharify

## Description
This is a playlist maker and organiser for music, using the API from Last.FM. We wanted to be able to create our own cloud service that performs similar actions to existing music platforms. Understanding the uses and advantages of having the freedom to create playlists to produce a particular desired musical atmosphere, and our project will deliver this.

Playlists are usually tied down to the platform that you're using, but this application will overcome that problem to provide users access to cross-platform playlists.

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

### Local

#### Pre-requisites

#### Steps

### Local Kubernetes

#### Pre-requisites

#### Steps

### GKE

#### Pre-requisites

#### Steps
