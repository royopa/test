import pymongo
import datetime

mongo_host = pymongo.MongoClient('mongodb://bmorier:Ghc955maxmax!@cluster0.mongodb.net/test_old') #

#client = pymongo.MongoClient("mongodb+srv://kay:myRealPassword@cluster0.mongodb.net/test_old")
client = pymongo.MongoClient('mongodb://bmorier:Ghc955maxmax!@cluster0-shard-00-00-qqmce.mongodb.net:27017,cluster0-shard-00-01-qqmce.mongodb.net:27017,cluster0-shard-00-02-qqmce.mongodb.net:27017/test_old?ssl=true&replicaSet=cluster0-shard-0&authSource=admin&retryWrites=true')
mongo_host=client

db=mongo_host.test

post = {"author": "Mike",
"text": "My first blog post!",
"tags": ["mongodb", "python", "pymongo"],
"date": datetime.datetime.utcnow() }


db.test1.insert_one(post)


