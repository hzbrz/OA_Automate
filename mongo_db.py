import pymongo, pprint

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["oadb1"]

# this func combines all the items of same categories and makes a better dictionary for checking for duplicates
def create_db_dict(databse):
  products_list = []
  test = {"electronics": {}, "toys": {}, "books": {}}
  elec = []
  toys = []
  books = []
  walmart_collection = databse["walmart_products"]
  for products in walmart_collection.find():
    products_list.append(products)

  for i in range(len(products_list)):
    try:
      elec.append(products_list[i]["electronics"])
    except KeyError:
      try:
        toys.append(products_list[i]["toys"])
      except KeyError:
        books.append(products_list[i]["books"])

  for i in elec:
    for k, v in i.items():
      test["electronics"][k] = v
  for i in toys:
    for k, v in i.items():
      test["toys"][k] = v
  for i in books:
    for k, v in i.items():
      test["books"][k] = v

  return test


# test_dict = create_db_dict(mydb)
# test = mydb["test_coll"]
# test.insert(test_dict, check_keys=False)
