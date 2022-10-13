---
title: Czas Kultury DOI
description: General info, notes and worklog
---

# Contents

- [General concept](#General concept)
- [Tasks](#Tasks)
- [Notes](#Notes)
- [Worklog](#Worklog)
  - [Basic Jira <-> GCP connection](#Worklog#Basic Jira <-> GCP connection)
  - [GCP -> Jira](#Worklog#GCP -> Jira)
  - [Jira -> GCP](#Worklog#Jira -> GCP)

# General concept

* Jira Cloud custom ScriptRunner button with webhook to *Pub/Sub*
* *Cloud Function*:
	* subscription to event
	* getting DOI
	* saving to issue by POST edit
* Authentication:
	* Jira -> GCP: service account api key? *Cloud Endpoints* with api key
	* GCP -> Jira: single user api key? (Justyna) secure it!
* (optional) creating entry in some database (*Firestore*/*Datastore*?)
* (optional) *App Engine* browser of past requests


# Tasks

- [o] [Basic Jira <-> GCP connection](#Basic Jira <-> GCP connection):
	- [X] ~~create Pub/Sub topic as HTTP endpoint~~
	- [X] ~~create simple function logging the request~~
	- [ ] create simple *Cloud Run* service
	- [ ] send example message with `curl`
	- [X] ~~create Jira SR button sending request to above Pub/Sub~~
	- [ ] create Jira SR button sending request to above Cloud Run
	- [X] move secrets from source code to Secret Manager

- [o] [GCP -> Jira](#GCP -> Jira):
	- [X] add a comment in the issue sending request
	- [ ] add/edit customfield value in the issue
	- [X] secure Jira key (*Secret Manager*?)

- [ ] [Jira -> GCP](#Jira -> GCP):
	- [ ] find a better way to authenticate user (*Cloud Endpoints* with API key?)
	- [ ] move article code to package for reusage purposes
	- [ ] create function subscribing to the event
	- [ ] getting article from jira issue sending the request

- [ ] Getting DOI:
	- [ ] getting DOI from test environment (or faking it)

- [ ] Saving DOI to Jira issue:
	- [ ] ???


# Notes
Securing PubSub with *Cloud Endpoints*: https://medium.com/google-cloud/secure-pubsub-push-with-cloud-endpoints-6a1adc36db9f


# Worklog
## Basic Jira <-> GCP connection
Function code example from (https://github.com/GoogleCloudPlatform/python-docs-samples/tree/main/functions/v2/pubsub)
```
gcloud config set functions/region europe-central2
gcloud config set functions/gen2 true
gcloud pubsub topics create doi-request
gcloud functions deploy doi-request-test --runtime=python310 --source=function-doi-request-test --entry-point=subscribe --trigger-topic=doi-request
```

Sending example message with `curl` (base64 encoding):
```
(echo -n '{"messages":[{"data":"'; echo -n "Friend" | base64 -w 0; echo -n '"}]}') | curl -X POST -H "Authorization: Bearer "$(gcloud auth print-access-token) -H "Content-Type: application/json; charset=utf-8" -d @- https://pubsub.googleapis.com/v1/projects/czk-tools/topics/doi-request:publish
```

SR button code (authorization token is temporary) in `jira-pf-generate-doi.groovy`.

Added secrets to GCP Secret Manager.

## Migrating to Cloud Run
Because the only way to access *Pub/Sub* from the outside with API key is through Endpoints -> App Engine -> Pub/Sub above plan makes no sense! If we are using App Engine it's better to stay there. Hence the idea of using plain Run service. There could be the same problem but... well.. let's try it anyway!

After creating basic service code add secrets by exporting YAML:
```
gcloud run services describe $SERVICE_NAME --format export >> ./run-doi-request-test/service.yaml
```

Then add envs in container config:
```
spec:
  ...
  template:
    ...
    spec:
      ...
      containers:
      - image: ...
        ...
        env:
        - name: JIRA_CZK_USER
          valueFrom:
            secretKeyRef:
              key: latest
              name: jira-czk-user
        - name: JIRA_CZK_KEY
          valueFrom:
            secretKeyRef:
              key: latest
              name: jira-czk-key
```

Increase revision number, make sure user has secret acces and then:
```
gcloud run services replace ./run-doi-request-test/service.yaml
```

## Configuring Endpoints - old
Via: (https://medium.com/google-cloud/secure-cloud-run-cloud-functions-and-app-engine-with-api-key-73c57bededd1)
Create account, add permissions:
```
gcloud iam service-accounts create endpoint-doi
gcloud projects add-iam-policy-binding czk-tools --role roles/servicemanagement.configEditor --member serviceAccount:endpoint-doi@czk-tools.iam.gserviceaccount.com
```
... Breaking and ditching this method, it's from 2019.


## Configuring endpoints (ESP2)
Via: (https://cloud.google.com/endpoints/docs/openapi/set-up-cloud-run-espv2)

OpenAPI file: `endpoints/openapi.yaml`

... It seems overkill (Endpoint is self-managed thins), let's switch again.


## Configuring API Gateway
Via: (https://cloud.google.com/api-gateway/docs/get-started-cloud-run)

OpenAPI file: `apigateway/openapi.yaml`

Creating:
```
gcloud api-gateway api-configs create hello-config \
  --api=hello-api --openapi-spec=apigateway/openapi.yaml \
  --project=czk-tools --backend-auth-service-account=doi-307@czk-tools.iam.gserviceaccount.com
```

Deploying:
```
gcloud api-gateway gateways create hello-gateway \
  --api=hello-api --api-config=hello-config \
  --location=europe-west1 --project=czk-tools
```
(API Gateway is available in `europe-west2` (London) and `europe-west1` (Belgium) only at this moment.)

Done the same steps but for run with not allowed unauthenticated. Service account is needed with *Cloud Run Invoker* role.

## GCP -> Jira

## Jira -> GCP
