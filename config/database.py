from pymongo import MongoClient

client = MongoClient("mongodb+srv://JPMC2022:JPMC260802@cluster0.ixfbrh2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = client.users

collection_name = db["messages"]
