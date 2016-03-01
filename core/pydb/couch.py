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

# Apply functions on to the database
def each_do(db,func,**kwargs):
	n = 1
	for _id in db:
		func(db.get(_id))
		n+=1
		if 'limit' in kwargs and n>kwargs['limit']:
			print('Limit of {0} records reached.'.format(kwargs['limit']))
			break

def iter(db,**kwargs):
	for _id in db:
		yield db.get(_id)
		