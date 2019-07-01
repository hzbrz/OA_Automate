from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from secrets import dynamic_link, toys, books, electronics
import time, pyperclip

# main driver
driver = webdriver.Chrome()
# goes to the initial link
driver.get(dynamic_link)

# dynamic link belongs to category 1, whatever intial link is
category = 1


# counter for pagination used to check and update the link to navigate
page_counter = 0

next_page_link = ""
item_counter = 0
while(True):
  # locating the main products on the page
  try:
    product_div = driver.find_element_by_id("searchProductResult")
  except NoSuchElementException:
    print("No more pages in this category")
    # setting it to the next category program id, this tracks which category the program is on as well 
    # as avoids going back to the initial dynamic_link and sticks to the next_page_link
    category = category + 1
    # changing to the category_id to the new category's id
    if category == 2:
      next_page_link = next_page_link.replace("cat_id="+electronics, "cat_id="+toys)
    elif category == 3:
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
  # this is to reach the page where we are out of items and we can move on to the other category
  li_items = ul.find_elements_by_class_name("Grid-col")[:2]
  
  # getting inside the list item so I can get more data for each item
  li_inner = li_items[item_counter].find_element_by_class_name("search-result-gridview-item")

  # getting the name 
  product_name = li_inner.find_element_by_class_name("product-title-link").get_attribute("title")

  # getting the item link to its details page
  product_link = li_inner.find_element_by_class_name("product-title-link").get_attribute("href")

  # getting the item price
  item_price = li_inner.find_element_by_class_name("price-group").get_attribute("aria-label")

  # ------------------------- TODO: generateTab func ---------------------------------------
  ## 2: I get the company name by opening a new tab in the same window, process is faster
  # opens a new empty tab
  driver.execute_script("window.open('');")
  time.sleep(.5)
  # Switches the driver focus to the new window
  driver.switch_to.window(driver.window_handles[1])
  # navigate to the prouct details page
  driver.get(product_link)
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
  #---------------------------------------------------------------------------------------
  print(product_name, "\n", item_price, "\n", product_link, "\n", company_name, "\n------------")

  # need to increment here to not run into the IndexError
  item_counter = item_counter + 1
  
  # print("line 87\n", page_counter, next_page_link)
  # hook to see if all items have been scraped on the page and use it to navigate to next page
  if item_counter == len(li_items[:2]):
    # setting item counter which lets me loop through the list to 0 after every page change otherwise the index is out of range
    item_counter = 0
    # incrementing the page number to match the links page number 
    page_counter = page_counter + 1
    # checking if it is first page and also the initial link, this is so taht the program can stay dynamic
    if page_counter == 1 and category == 1:
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

  
# TODO 1: figure out navigation between pages by changing the (dynamic_link) imported from secrets - hz 07/01
# TODO 2: switch to another category when there is no more products to scrape in one category - hz 07/02
# TODO 3: figure out optimal way to modify the link and automate moving categories -hz
# TODO 4: Put all product data in a dictionary, the key should be number or name?
# TODO 4: turn code into componenets through functions (GENERAL GOAL)

driver.close()

