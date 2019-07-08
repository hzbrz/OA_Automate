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

count = 0
# dictionary that has the name and the barcode for easy access after finding closest match
matching_dict = {}
possible_match = []
# print(len(upc_request_urls))
for item_name in upc_request_urls[:1]:
  res = requests.get("https://www.barcodelookup.com/"+item_name)
  res.raise_for_status()
  soup = bs4.BeautifulSoup(res.text[3700:], "html.parser")
  ul = soup.select("#product-search-results")
  li = ul[0].select('li > div > p')
  while count < len(li):
    title = li[count].getText()
    # getText() gets - Barcode: number, (Barcode:) part is eliminated after 9th char
    barcode = li[count+1].getText()[9:]
    matching_dict[title] = barcode
    possible_match.append(title)
    count = count + 4
  # difflib.get_close_matches(word, possibilities, n, cutoff) - cutoff is a range between 0-1, possiblilites
  # for the match have to atleast meet the cutoff
  title_to_match = item_name.replace('-', " ")
  closest_match = get_close_matches(title_to_match, possible_match, 2, 0.7)
  for i in closest_match:
    print(matching_dict[i])


