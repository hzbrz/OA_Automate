import pymongo, pprint

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["oadb1"]

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
      pprint.pprint("elelc")
    except KeyError:
      try:
        toys.append(products_list[i]["toys"])
        print("je;;p")
      except KeyError:
        books.append(products_list[i]["books"])
        print('bppls')

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
