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
	# Update if the record has already been existed
	mapper = '''function(doc){{ 
		if(doc.topic_id={0}) 
			emit(doc.id,null)}}'''.format(record['topic_id'])
	if len(db.query(mapper))==0:
		_id, _rev = db.save(record)
	else:
		# Replace the existing document
		_id = [r.id for r in db.query(mapper)][0]
		existing = db.get(_id)
		for attr in record:
			if attr not in ['_id','_rev']:
				existing[attr] = record[attr]
		_id, _rev = db.save(existing)

	return (_id,_rev)