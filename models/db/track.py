import logging
import re

import gdata.youtube
import gdata.youtube.service
import gdata.alt.appengine

from calendar import timegm

from google.appengine.ext import db
from google.appengine.api.taskqueue import Task

from models.db.user import User
from models.db.station import Station
from models.db.counter import Shard

COUNTER_OF_VIEWS_PREFIX = "track.views."

class Track(db.Model):
	youtube_id = db.StringProperty(required = True)
	admin = db.BooleanProperty(default = False, required = True)
	station = db.ReferenceProperty(Station, required = True, collection_name = "trackStation")
	user = db.ReferenceProperty(User, required = True, collection_name = "trackUser")
	created = db.DateTimeProperty(auto_now_add = True)

	@staticmethod
	def get_extended_tracks(tracks):
		extended_tracks = []
		youtube_ids = []
		
		if(tracks):
			for track in tracks:
				youtube_ids.append(track.youtube_id)
		
			youtube_tracks = Track.get_youtube_tracks(youtube_ids)
		
			for track, youtube_track in zip(tracks, youtube_tracks):
				if(youtube_track):
					extended_tracks.append({
						"track_id": track.key().id(),
						"track_created": timegm(track.created.utctimetuple()),
						"track_admin": track.admin,
						"youtube_id": youtube_track["id"],
						"youtube_title": youtube_track["title"],
						"youtube_duration": youtube_track["duration"],
					})
				else:
					extended_tracks.append(None)
		
		return extended_tracks

	@staticmethod
	def get_or_insert_by_youtube_id(youtube_id, station, user_proxy, admin):
		user = user_proxy.user
		track = None
		extended_track = None
		youtube_track = None
		
		if(youtube_id):
			# We check if the track has not been submitted by the same user
			q = Track.all()
			q.filter("youtube_id", youtube_id)
			q.filter("user", user.key())
			track = q.get()
			
			if(track):
				logging.info("Track on Phonoblaster")
				extended_track = Track.get_extended_tracks([track])[0]

			# It's the first time the track is submitted by the user
			else:
				logging.info("Track not on Phonoblaster")
				youtube_track = Track.get_youtube_tracks([youtube_id])[0]
			
				# If track on Youtube, save the track on Phonoblaster, generate the extended track
				if(youtube_track):
					logging.info("Track on Youtube")
					track = Track(
						youtube_id = youtube_id,
						station = station,
						user = user,
						admin = admin,
					)
					track.put()
					logging.info("New track put in the datastore.")
				
					extended_track = {
						"track_id": track.key().id(),
						"track_created": timegm(track.created.utctimetuple()),
						"track_admin": track.admin,
						"youtube_id": youtube_track["id"],
						"youtube_title": youtube_track["title"],
						"youtube_duration": youtube_track["duration"],
					}
		
		return (track, extended_track)


	@staticmethod
	def get_youtube_tracks(youtube_ids):
		youtube_tracks = []
		
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
					youtube_tracks.append(None)
				else:
					id = re.sub(r"http://gdata.youtube.com/feeds/api/videos/","", entry.id.text)
					title = entry.title.text
					duration = int(entry.media.duration.seconds)
					
					youtube_tracks.append({
						"id": id,
						"title": title,
						"duration": duration,
					})
		
		return youtube_tracks	
	
	
	@staticmethod
	def number_of_views(track_id):
		shard_name = COUNTER_OF_VIEWS_PREFIX + str(track_id)
		count = Shard.get_count(shard_name)
		return count
	
	@staticmethod
	def increment_views_counter(track_id):
		shard_name = COUNTER_OF_VIEWS_PREFIX + str(track_id)
		
		task = Task(
			url = "/taskqueue/counter",
			params = {
				"shard_name": shard_name,
				"method": "increment"
			}
		)
		task.add(queue_name = "counters-queue")
	
	
	