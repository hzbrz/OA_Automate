from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from secrets import dynamic_link
import time, pyperclip

# main driver
driver = webdriver.Chrome()
# goes to the initial link
driver.get(dynamic_link)


# locating the main products on the page
product_div = driver.find_element_by_id("searchProductResult")

# getting the list of all items in the page
ul = product_div.find_element_by_class_name("search-result-gridview-items")

# getting all list items that contain each item
li_items = ul.find_elements_by_class_name("Grid-col")

for li in li_items:
  # getting inside the list item so I can get more data for each item
  li_inner = li.find_element_by_class_name("search-result-gridview-item")

  # getting the name 
  product_name = li_inner.find_element_by_class_name("product-title-link").get_attribute("title")

  # getting the item link to its details page
  product_link = li_inner.find_element_by_class_name("product-title-link").get_attribute("href")

  # getting the item price
  item_price = li_inner.find_element_by_class_name("price-group").get_attribute("aria-label")

  # # TWO WAYS TO DO THE SAME THING:

  # ## 1: I get the company name in this method by opening a new window which caused the connection to temporarily timeout
  # # creating another driver to bypass a stale element exception/issue
  # driver_two = webdriver.Chrome()
  # # navigating to the product's details page
  # driver_two.get(product_link)
  # # locating the area of the page for the company name for the product
  # # learned: to get the text in a span tag, you can jsut call the text method on the parent element
  # company_name = driver_two.find_element_by_class_name("prod-brandName").get_attribute('text')
  # # navigating back to the page with all other products and repeating process
  # driver_two.close()

  ## 2: I get the company name by opening a new tab in the same window, process is faster
  # opens a new empty tab
  driver.execute_script("window.open('');")
  time.sleep(.5)
  # Switches the driver focus to the new window
  driver.switch_to.window(driver.window_handles[1])
  # navigate to the prouct details page
  driver.get(product_link)
  # locating the area of the page for the company name for the product and getting the company name
  company_name = driver.find_element_by_class_name("prod-brandName").get_attribute('text')
  # close the active tab
  driver.close()
  # Switch the focus back to the first tab
  driver.switch_to.window(driver.window_handles[0])
  time.sleep(.5)

  print(product_name, "\n", item_price, "\n", product_link, "\n", company_name, "\n------------")


# TODO 1: figure out navigation between pages by changing the (dynamic_link) imported from secrets - hz 07/01
# TODO 2: switch to another category when there is no more products to scrape in one category - hz 07/02
# TODO 3: figure out optimal way to modify the link and automate moving categories -hz
# TODO 4: turn code into componenets through functions (GENERAL GOAL)

driver.close()

