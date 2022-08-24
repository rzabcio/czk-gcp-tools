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

- [X] [Basic Jira <-> GCP connection](#Basic Jira <-> GCP connection):
	- [X] create Pub/Sub topic as HTTP endpoint
	- [X] create simple function logging the request
	- [X] send example message with `curl`
	- [X] create Jira SR button sending request to above Pub/Sub
	- [X] move secrets from source code to Secret Manager

- [.] [GCP -> Jira](#GCP -> Jira):
	- [X] add a comment in the issue sending request
	- [ ] add/edit customfield value in the issue
	- [ ] secure Jira key (*KMS*?)

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
gcloud functions deploy doi-request-test --runtime=python310 --source=. --entry-point=subscribe --trigger-topic=doi-request
```

Sending example message with `curl` (base64 encoding):
```
(echo -n '{"messages":[{"data":"'; echo -n "Friend" | base64 -w 0; echo -n '"}]}') | curl -X POST -H "Authorization: Bearer "$(gcloud auth print-access-token) -H "Content-Type: application/json; charset=utf-8" -d @- https://pubsub.googleapis.com/v1/projects/czk-tools/topics/doi-request:publish
```

SR button code (authorization token is temporary) in `jira-pf-generate-doi.groovy`.

Added secrets to GCP Secret Manager.


## GCP -> Jira

## Jira -> GCP
