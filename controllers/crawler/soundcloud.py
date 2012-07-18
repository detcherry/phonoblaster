import webapp2
import json
import re
import urllib
import logging

class SoundcloudCrawlerHandler(webapp2.RequestHandler):
	def get(self, permalink):
		permalink_url = "http://soundcloud.com/" + permalink
		twitter = None
		
		file = urllib.urlopen(permalink_url)
		try:
			page = file.read()
		finally:
			file.close()
					
		result = re.search(r'a\shref=\"https?:\/\/w?w?w?\.?twitter\.com\/?#?!?\/(\w+)\"\sclass=\"twitter\s\"', page)
		if(result):
			twitter = result.group(1)
				
		response = {
			"twitter" : twitter,
		}
		
		self.response.out.write(json.dumps(response))