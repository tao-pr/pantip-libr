"""
Model serialiser with MongoDB
@starcolon projects
"""

import pymongo
from pymongo import MongoClient
from pymongo import InsertOne

def new(host,db,coll):
  conn = {}
  conn['addr']  = "mongodb://{0}:27017/".format(host)
  conn['mongo'] = MongoClient(addr)
  conn['db']    = self.mongo[db]
  conn['src']   = self.db[coll]
  return conn

def save(conn,data):
  conn['src'].insert_one(data)

def clear(conn):
  conn['src'].find_one_and_delete({})

def load(conn):
  return conn['src'].find_one(sort=[('_id', pymongo.DESCENDING)])
