## Required Packages:

C:

libxml2,
libsxlt

Python:

django,
lxml,
newspaper,
textblob,
pytz,
MySQL-python,
dateutil


## Collect data from Google news and Twitter search API

demoBasic/DataCollector/main.py

Note: 

1. Requires keys to access Twitter search API

2. Requires a running DBpedia Spotlight server at localhost

## Dump data to mysql

demoBasic/DataCollector/DB.py

## Core modules in web application

### Event hierarchy construction Code

function pLSABet in tweenews/overviews/lib/pLSABet.py

### Linking and summarization 

function summarization in tweenews/overviews/lib/summarization.py

### Django entry point

function event_running in tweenews/overviews/views/event_view.py

## Start web application

Run server:

python tweenews/overviews/manage.py runserver 0.0.0.0:XXXX

Open webpage at localhost:

http://localhost:XXXX/overviews/event_discovery/

