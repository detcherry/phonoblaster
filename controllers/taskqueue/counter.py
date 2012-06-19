import webapp2

from models.db.counter import Shard

class CounterHandler(webapp2.RequestHandler):
	def post(self):
		shard_name = self.request.get("shard_name")
		method = self.request.get("method")
		
		if(method == "increment"):
			Shard.increment(shard_name)
		else:
			Shard.decrement(shard_name)
