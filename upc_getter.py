# this program is to get upc for the scraped items for a better comparison of items on amazon
from difflib import get_close_matches
from selenium import webdriver
from secrets import upc_checker
from mongo_db import mydb, create_db_dict
import requests, bs4, time

# use request for this one nto selenium 
# sample link https://www.barcodelookup.com/Monopoly-Game ... url + item_name where whitespaces are joined with -

walmart_products_dict = create_db_dict(mydb)
upc_request_urls = []
for k, v in walmart_products_dict["electronics"].items():
  # [n for n in item if (expression testing if it hasm the character)]
  bad_chars = ''.join(c for c in k if c not in "%!(){}<>\"\",+/\\#&'")
  whitespace_to_hyphen = bad_chars.replace(" ", "-")
  upc_request_urls.append(whitespace_to_hyphen)

for k, v in walmart_products_dict["toys"].items():
  bad_chars = ''.join(c for c in k if c not in '%!(){}<>\"\",+/\\#&')
  whitespace_to_hyphen = bad_chars.replace(" ", "-")
  upc_request_urls.append(whitespace_to_hyphen)

for k, v in walmart_products_dict["books"].items():
  bad_chars = ''.join(c for c in k if c not in '%!(){}<>\"\",+/\\#&')
  whitespace_to_hyphen = bad_chars.replace(" ", "-")
  upc_request_urls.append(whitespace_to_hyphen)

for item_name in upc_request_urls:
  res = requests.get("https://www.barcodelookup.com/"+item_name)
  res.raise_for_status()
  print("success")

