# Scraper for https://anonymsms.com/
Scraper collects sms messages not older than 5 minutes from https://anonymsms.com/ and sends them to https://dev.7sim.cc/in.

## Installation

Cloning a repository:

```git clone https://github.com/shestakovitch/anonymsms_parser.git```

Creating a virtual environment:

```python3 -m venv venv```


Activating the virtual environment:

```source venv/bin/activate```

Installing the required packages from requirements.txt﻿:

```pip3 install -r requirements.txt```

## Configuration

1. Rename .env_example to .env, assign your SMS token to the SMS_TOKEN variable.
2. In config.py by default set the time for which the proxy is excluded from bypass in case of blocking BLOCK_TIME=1800 (30 minutes), if necessary - change the value.
3. Add the file with proxies “proxies.txt” to the root folder.
4. Run main.py.
