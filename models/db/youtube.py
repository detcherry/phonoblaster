import logging
import re

import gdata.youtube
import gdata.youtube.service
import gdata.alt.appengine

class Youtube():
	
	@staticmethod
	def get_extended_tracks(youtube_ids):
		extended_tracks = []

		# Create a Youtube client and run it on App Engine
		client = gdata.youtube.service.YouTubeService()
		gdata.alt.appengine.run_on_appengine(client)

		# Build the batch query
		query = "<feed xmlns=\"http://www.w3.org/2005/Atom\""
		query += " xmlns:media=\"http://search.yahoo.com/mrss/\""
		query += " xmlns:batch=\"http://schemas.google.com/gdata/batch\""
		query += " xmlns:yt=\"http://gdata.youtube.com/schemas/2007\">"
		query += "<batch:operation type=\"query\"/>"

		for youtube_id in youtube_ids:
		    query += ("<entry><id>http://gdata.youtube.com/feeds/api/videos/%s</id></entry>" % youtube_id)

		query += "</feed>"

		# Send the batch query
		uri = 'http://gdata.youtube.com/feeds/api/videos/batch'		
		feed = client.Post(query, uri, converter=gdata.youtube.YouTubeVideoFeedFromString)

		if(feed.entry):
			for entry in feed.entry:

				skip = False
				for x in entry.extension_elements:
					if x.tag == "status" and x.namespace == "http://schemas.google.com/gdata/batch" and x.attributes["code"] != "200":
						skip = True

				if(skip):
					extended_tracks.append(None)
				else:
					id = re.sub(r"http://gdata.youtube.com/feeds/api/videos/","", entry.id.text)
					title = entry.title.text
					duration = int(entry.media.duration.seconds)

					extended_tracks.append({
						"id": id,
						"title": title,
						"duration": duration,
					})

		return extended_tracks
		
	
	