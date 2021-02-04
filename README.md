# Checkers Scraper
Scrape all products listed on the Checkers store website.

## Guide
All the links have been downloaded to a json file in the `links` directory. The scraper will loop through each
category and store the item to `food_scraper.db` for easier access.

There are two main methods to run, they are `setup_db()` if you want to start from scratch
and `loop_links()` which will run through all the links in `links.json`.

```bash
$ pip install -r requirements.txt
$ python main.py
```

## Why I wrote this
Wanted to prove a web-scraper can be done using light weight packages and not rely on `bs4`

### What do I plan on using this information for?
Create a custom Alexa grocery skill that will help suggest best price alternative and keep track of my monthly spending 
without needing to save the receipts. 