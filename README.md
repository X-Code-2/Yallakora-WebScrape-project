YallaKora WebScrape Project

This project is a simple Python script that scrapes football match data from YallaKora for a specific date and saves the results into a CSV file. It extracts match type, teams, match time, and final score, then stores the data in a clean, structured format.

Features

Scrapes match data from YallaKora Match Center

Extracts teams, match time, match type, and score

Saves all results into matches.csv

Simple and easy to run

Requirements

Python 3

requests

beautifulsoup4

lxml

pyfiglet

How to Run

Run the script with a date in the format MM/DD/YYYY:

python yallakora.py 11/13/2025

A CSV file will be created automatically with the scraped results.

Notes

If YallaKora changes its page structure, the scraper may need updates to continue working.

License

MIT License
