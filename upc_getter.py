# this program is to get upc for the scraped items for a better comparison of items on amazon
# from difflib import get_close_matches not using this anymore some of the closest upc matches dont work
from selenium import webdriver
from secrets import upc_checker
from mongo_db import mydb, create_db_dict
import requests, bs4, time

start_time = time.time()
# creatng new collection
barcodes_for_amazon = mydb["barcodes_amazon"]
# wiping data for new data, not appending
barcodes_for_amazon.delete_many({})

# general dict for all items
walmart_products_dict = create_db_dict(mydb)
# arr for the webstie friendly url for to pass into requests
upc_request_urls = []
# 3 arrs bellow trun whitespace to hyphen
for k, v in walmart_products_dict["electronics"].items():
  whitespace_to_hyphen = k.replace(" ", "-")
  upc_request_urls.append(whitespace_to_hyphen)

for k, v in walmart_products_dict["toys"].items():
  whitespace_to_hyphen = k.replace(" ", "-")
  upc_request_urls.append(whitespace_to_hyphen)

for k, v in walmart_products_dict["books"].items():
  whitespace_to_hyphen = k.replace(" ", "-")
  upc_request_urls.append(whitespace_to_hyphen)

# dictionary that has the name and the barcode for easy access after finding closest match
matching_dict = {}
possible_match_barcodes = []
print(len(upc_request_urls))
for item_name in upc_request_urls:
  # counter to keep track of the barcodes 
  count = 0
  # request to the webpage
  res = requests.get(upc_checker+item_name)
  # checking for 200, false = program stop
  res.raise_for_status()
  # truning part of it into soup object
  soup = bs4.BeautifulSoup(res.text[3700:], "html.parser")
  ul = soup.select("#product-search-results")
  # getting all li's
  li = ul[0].select('li > div > p')
  key = item_name.replace("-", " ")
  # looking for the word Barcode within the first 7 items of the array and then getting the barcode from that
  arr = [n.getText()[9:] for n in li[:7] if "Barcode: " in n.getText()]
  print(key, arr)
  matching_dict[key] = arr

# creating new collection of the dictionary of barcodes
barcodes_for_amazon.insert(matching_dict, check_keys=False)
print("barcodes inserted")

elapsed_time = time.time() - start_time
print(elapsed_time/60)
