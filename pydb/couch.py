"""
CouchDB connector for Pantip-libr
@starcolon projects
"""

from couchdb.client import Server

def connector(collection):
	# Make a server connection
	srv = Server()
	db  = srv.create(collection)
	return db

def push(db,record):
	_id, _rev = db.save(record)
	return (_id,_rev)