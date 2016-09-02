"""
Model serialiser with MongoDB
@starcolon projects
"""

import pymongo
from pymongo import MongoClient
from pymongo import InsertOne

def new(host,db,coll):
  conn = {}
  conn['mongo'] = MongoClient("mongodb://{0}:27017/".format(host))
  conn['db']    = conn['mongo'][db]
  conn['src']   = conn['db'][coll]
  return conn

def save(conn,data):
  conn['src'].insert_one(data)

def clear(conn):
  conn['src'].find_one_and_delete({})

def load(conn):
  return conn['src'].find_one(sort=[('_id', pymongo.DESCENDING)])
