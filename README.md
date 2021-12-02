# walletscanner

## Intro
A small python package that utilizes the https://www.covalenthq.com/ endpoint to scan different wallet adresses. This is primarily made to help crypto holders gain a overview of their total holdings even when it is split across different wallets, networks and tokens.

## How to
In the config/ their is a folder containing a config-template file that is used to fill in the information regarding the wallets that one wishes to scan

## Launch

Use command gunicorn index:server -b :5000 -name walletscanner --workers 2  --daemon
