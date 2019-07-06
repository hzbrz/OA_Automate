from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from secrets import dynamic_link, toys, books, electronics
from mongo_db import mydb, create_db_dict
import time, pyperclip, pprint

# main driver
driver = webdriver.Chrome()
# goes to the initial link
driver.get(dynamic_link)

# dynamic link belongs to category 0, whatever intial link is
category = 0
# counter for pagination used to check and update the link to navigate
page_counter = 0
# next page link global var
next_page_link = ""
# item_counter to track if all items in page has been scraped
item_counter = 0

# electronics dictionary holds electronics data
electronics_dict = {"electronics": {}}
# toys dictionary holds all toys data
toys_dict = {"toys": {}}
# books dictionary holds all books data
books_dict = {"books": {}}

# func creates a new tab and goes to the product details page and returns the company name
def create_new_tab(detail_page_link):
  # I get the company name by opening a new tab in the same window, process is faster
  # opens a new empty tab
  driver.execute_script("window.open('');")
  time.sleep(.5)
  # Switches the driver focus to the new window
  driver.switch_to.window(driver.window_handles[1])
  # navigate to the prouct details page
  driver.get(detail_page_link)
  time.sleep(.5)
  # locating the area of the page for the company name for the product and getting the company name
  try:
    # the try-atch is due to walmart sometimes not being able to load the product details page
    company_name = driver.find_element_by_class_name("prod-brandName").get_attribute('text')
  except NoSuchElementException:
    print("company name page bugged out")
    company_name = "couldn't find"
  # close the active tab
  driver.close()
  # Switch the focus back to the first tab
  driver.switch_to.window(driver.window_handles[0])
  time.sleep(.5)

  return company_name

# getting the walmart products collection for the mongodb database, I will use this to insert and check for products
# that already been inserted
walmart_collection = mydb["walmart_products"]

# going to use this list which will hold the dictionary from the db and use it to check for keys that exist in db already
products_list = []
walmart_collection = mydb["walmart_products"]
for products in walmart_collection.find():
  products_list.append(products)

# category checking and populating my ditionaries, and checking in the databse if an item exists so that I do not put in same items
def create_dicts(walmart_cat, item_name, item_price, link, company_name):
  # if the database is not empty, then go ahead and compare for selective insertions
  if len(products_list) > 0:
    # if category is electrionics and if the item is already not inserted in the databse then put it in the dictionary
    if walmart_cat == 0 and item_name not in products_list[0]["electronics"]:
      electronics_dict["electronics"][item_name] = {"price": item_price, "link": link, "company": company_name}
    elif walmart_cat == 1 and item_name not in products_list[1]["toys"]:
      toys_dict["toys"][item_name] = {"price": item_price, "link": link, "company": company_name}
    elif walmart_cat == 2 and item_name not in products_list[2]["books"]:
      books_dict["books"][item_name] = {"price": item_price, "link": link, "company": company_name}
    else:
      print(item_name, " data already exists in db")  
  else:
    print("no items in database yet")
    # first time population of databse, not checking if items exist because databse is empty
    if walmart_cat == 0:
      electronics_dict["electronics"][item_name] = {"price": item_price, "link": link, "company": company_name}
    elif walmart_cat == 1:
      toys_dict["toys"][item_name] = {"price": item_price, "link": link, "company": company_name}
    elif walmart_cat == 2 :
      books_dict["books"][item_name] = {"price": item_price, "link": link, "company": company_name}
  

while(True):
  # this try-catch is used to check if the category has any more items left to scrape, if not then go to next cat
  try:
    # locating the main products on the page
    product_div = driver.find_element_by_id("searchProductResult")
  except NoSuchElementException:
    print("No more pages in this category")
    # setting it to the next category program id, this tracks which category the program is on as well 
    # as avoids going back to the initial dynamic_link and sticks to the next_page_link
    category = category + 1
    # changing to the category_id to the new category's id
    if category == 1:
      next_page_link = next_page_link.replace("cat_id="+electronics, "cat_id="+toys)
    elif category == 2:
      next_page_link = next_page_link.replace("cat_id="+toys, "cat_id="+books)
    else:
      # if no more categories as of now then get out of the loop and end program
      break
    page_no = next_page_link.find(str(page_counter+1), 245, 254)
    # setting the page_counter back to 0 becasue in a new category
    page_counter = 0
    # setting page number back to 1 because in new cat
    next_page_link = next_page_link.replace("page="+next_page_link[page_no], "page=1")
    # navigating to the new category
    driver.get(next_page_link)
    # re-setting back the product_div element to avoid NoSuchElementException
    product_div = driver.find_element_by_id("searchProductResult")  
  
  # getting the list tag
  ul = product_div.find_element_by_class_name("search-result-gridview-items")
  
  # getting all list items that contain each item, also putting this inside the while so the list updates every loop
  li_items = ul.find_elements_by_class_name("Grid-col")[:4]
  
  # getting inside the list item so I can get more data for each item
  li_inner = li_items[item_counter].find_element_by_class_name("search-result-gridview-item")

  # getting the name 
  product_name = li_inner.find_element_by_class_name("product-title-link").get_attribute("title")

  # getting the item link to its details page
  product_link = li_inner.find_element_by_class_name("product-title-link").get_attribute("href")

  # getting the item price
  item_price = li_inner.find_element_by_class_name("price-group").get_attribute("aria-label")
  
  # capturing the func returned company name
  company_name = create_new_tab(product_link)

  # func to create the dictionaries storing data
  create_dicts(category, product_name, item_price, product_link, company_name)

  # need to increment here to not run into the IndexError
  item_counter = item_counter + 1

  # hook to see if all items have been scraped on the page and use it to navigate to next page
  if item_counter == len(li_items[:4]):
    # setting item counter which lets me loop through the list to 0 after every page change otherwise the index is out of range
    item_counter = 0
    # incrementing the page number to match the links page number 
    page_counter = page_counter + 1
    # checking if it is first page and also the initial link, this is so taht the program can stay dynamic
    if page_counter == 1 and category == 0:
      # finding the page number and storing the index
      page_no = dynamic_link.find(str(page_counter), 245, 254)
      # creating the new link by replacing the (page=1) part of the link with my incremented counter
      # replacign the entire page=1 part because if I only do the number it will change other numbers as well
      next_page_link = dynamic_link.replace("page="+dynamic_link[page_no], "page="+str(page_counter+1))
      driver.get(next_page_link)
    else:
      page_no = next_page_link.find(str(page_counter), 245, 254)
      next_page_link = next_page_link.replace("page="+next_page_link[page_no], "page="+str(page_counter+1))
      # nav to next page
      driver.get(next_page_link)


electronics_insert = walmart_collection.insert(electronics_dict, check_keys=False)
toys_insert = walmart_collection.insert(toys_dict, check_keys=False)
books_insert = walmart_collection.insert(books_dict, check_keys=False)
print("\n--------------------------------------------------------------------")
print("data inserted")


# TODO 1: figure out navigation between pages by changing the (dynamic_link) imported from secrets - hz 07/01 - DONE
# TODO 2: switch to another category when there is no more products to scrape in one category - hz 07/02 - DONE
# TODO 3: figure out optimal way to modify the link and automate moving categories -hz - DONE
# TODO 4: Put all product data in a dictionary, the key should be number or name? - hz - DONE
          # data format:
          # category
              ## name
                 ### price
                 ### product link
                 ### company name
# TODO 5: Store dict local or in database or firebase (idk) - hz
# TODO GEN: turn code into componenets through functions (GENERAL GOAL)

driver.close()

