from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from mongo_db import mydb
from secrets import email_ap, password_ap, seller_product_page, user_agent
import pprint, requests, urllib, time

barcodes = mydb["barcodes_amazon"]
barcode_keys = []
barcode_vals = []
count = 1

for barcode_db in barcodes.find():
  for k, v in barcode_db.items():
    barcode_keys.append(k)
    barcode_vals.append(v)   


options = webdriver.ChromeOptions()
# options.add_argument("headless")
options.add_argument(f'user-agent={user_agent}')
# options.add_argument(f'--proxy-server={working_proxy}')

driver = webdriver.Chrome(chrome_options=options)
driver.get(seller_product_page)

# initial email input
email = driver.find_element_by_id("ap_email")
email.send_keys(email_ap)

password = driver.find_element_by_id("ap_password")
password.send_keys(password_ap)

# first submit to trigger captcha
submit = driver.find_element_by_id("signInSubmit")
submit.click()

# password becomes clear after page reload so needs to be re-entered
pass_2 = driver.find_element_by_id("ap_password")
pass_2.send_keys(password_ap)

# Custom Expected conditions to check for captcha and opt code
class captcha_is_filled(object):
  """An expectation for checking that my capctcha has been filled

  locator - used to find the element
  returns True once the captcha is equaling the length of 6 and then it moves on to clicking the button
  """
  def __init__(self, locator):
    self.locator = locator

  # method calls false if condition not met
  def __call__(self, driver):
    element = driver.find_element(*self.locator)   # Finding the referenced element
    if len(element.get_attribute("value")) == 6:
        return True
    else:
        return False

# Wait until my captcha is filled, which is it equal to having a length of 6
wait = WebDriverWait(driver, 20).until(captcha_is_filled((By.ID, 'auth-captcha-guess')))

# button clicked once my captcha is filled
submit_2 = driver.find_element_by_id("signInSubmit")
submit_2.click()

# waiting for the 2 step verification
# click on button once opt code is filled in and I use the same custom EC to check for that as well
wait_for_opt_code = WebDriverWait(driver, 30).until(captcha_is_filled((By.ID, 'auth-mfa-otpcode')))
submit_opt = driver.find_element_by_id("auth-signin-button")
submit_opt.click()

for i in range(len(barcode_keys[1:2])):
  print(barcode_keys[i+1], barcode_vals[i+1])
  driver.switch_to.window(driver.window_handles[0])
  time.sleep(3)
  search_class = driver.find_element_by_class_name("full-width")
  search_input = search_class.find_element_by_tag_name('input')
  search_input.send_keys(barcode_keys[i+1], Keys.ENTER)
  time.sleep(3)
  try:
    prodcut_results = driver.find_element_by_id("search-result")
  except:
    print("nothing on this page")

print("\n--------------------------------")

# first_search_prod = prodcut_results.find_element_by_class_name("row")
# print("found products")
# print(first_search_prod)
# except:
#   print("page showed no results")
#   driver.switch_to.window(driver.window_handles[0])
#   for barcode in barcode_vals[i+1]:
#     search_input.send_keys(barcode)
# while (count < len(barcode_keys)):
  # for barcode in barcode_vals[count: count+10]:
  #   print(barcode)
  # print("\n--------------------------------")

#   count = count + 10

