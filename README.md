# heroscript
Console tool for upload and edit activities to velohero and STRAVA.

# Preconditions

## Python
You need Python 3.x on your local machine.

## Velohero
You need a Velohero account, of course. Set up heroscript with the Single-Sign-On ID from Velohero / Hello / Single-Sign-On / Single Sign On ID. For instance: 

$ heroscript config --velohero_sso_id kdRfmIHT6IVH1GI12345BIhaUpwTaQguuzE7FFs4

## STRAVA
For STRAVA, you need an to create an API whith a call back domain 'localhost'. From this API, you need the client ID and the Client Secret. Configure heroscript with this values:

$ heroscript config --strava_client_id 12345
$ heroscript config --strava_client_secret 509d7ed7ab29c93bb12345a05f3a1627c57e413f

## Local Web Server
A local webserver is used for STRAVA authentication. This server has a default port '4312' but can be chaned with the config command. For instance:

$ heroscript config --port 4444

# Setup

