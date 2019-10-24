# pastebin_scraper
Pastebin Scraper with web gui

## Setup
Install Python and the needed modules (requests, mysqldb, peewee)  
Setup mysql with a new database for the pastes
Setup apache with python cgi. Copy frontent/index.html into /www/html/ and the python files in frontend/ into /www/cgi-bin/

## Backend
The scraper.py file queries the pastebin.com API and stores them into the sql database. Make sure your ip address is whitelisted on pastebin.com

## Frontend
The Web GUI uses python-cgi to build the page, queries the sql database. 
