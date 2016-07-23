# IPRA Portal Scraper

This is a Python script that scrapes the [website](http://portal.iprachicago.org/) of Chicago's Independent Police Review Authority (IPRA) for information they have released on open investigations of police misconduct. 

This project supports the Invisible Institute's [Chicago Police Incidents Data repository](https://github.com/invinst/chicago-police-data), a public resource for police accountability and transparency. 

## Usage

### Scraping

In the main directory, run:

    python ipra_scraper.py

This will overwrite `most_recent_scrape.json`, and it will also save a copy with the date and time in the filename in the `scrapes/` directory. 

### Utilities

A few utilities are in the `data_utils.py` script. Below are terminal commands to use them:

Summarize a scrape:

    python data_utils.py summarize most_recent_scrape.json
    
Write CSV tables for a scrape:

    python data_utils.py writecsv most_recent_scrape.json
    
Compare two scrapes:

    python data_utils.py compare path_to_oldjson path_to_newjson

### Web viewer

A web json file viewer of the `most_recent_scrape.json` can be found at

* [https://jayqi.github.io/ipra-portal-scraper/](https://jayqi.github.io/ipra-portal-scraper/)

This was made using [mohsen1/json-formatter-js](https://github.com/mohsen1/json-formatter-js).