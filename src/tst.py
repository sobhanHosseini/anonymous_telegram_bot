import pymongo
from src.db import db

for doc in db.users.find():
    print(doc)
    print('-' * 50)