"""
CouchDB connector for Pantip-libr
@starcolon projects
"""

from couchdb.client import Server

def connector(collection):
	# Make a server connection
	svr = Server()
	if collection not in svr:
		return svr.create(collection)
	else:
		return svr[collection]

def push(db,record):
	_id, _rev = db.save(record)
	return (_id,_rev)