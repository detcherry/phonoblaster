import logging
from calendar import timegm

from google.appengine.ext import db
from google.appengine.api.taskqueue import Task

from models.db.station import Station
from models.db.counter import Shard
from models.db.youtube import Youtube

COUNTER_OF_VIEWS_PREFIX = "track.views."
COUNTER_OF_LIKES_PREFIX = "track.likes."

class Track(db.Model):
	youtube_id = db.StringProperty(required = False)
	youtube_title = db.StringProperty(required = False)
	youtube_duration = db.IntegerProperty(required = False)
	soundcloud_id = db.StringProperty(required = False)
	soundcloud_title = db.StringProperty(required = False)
	soundcloud_duration = db.IntegerProperty(required = False)
	soundcloud_thumbnail = db.StringProperty(required = False)
	station = db.ReferenceProperty(Station, required = True, collection_name = "trackStation")
	created = db.DateTimeProperty(auto_now_add = True)

	@staticmethod
	def get_or_insert(incoming, station):
		id = incoming["id"]
		title = incoming["title"]
		duration = incoming["duration"]
		
		track = None
		
		# This is a Youtube track
		if(incoming["type"]=="youtube"):
			# We check if the track is already owned by this station
			q = Track.all()
			q.filter("youtube_id", id)
			q.filter("station", station.key())
			track = q.get()
			
			if(track):
				logging.info("Track on Phonoblaster")
				
			# First time this track is submitted in this station
			else:
				logging.info("Track not on Phonoblaster")

				track = Track(
					youtube_id = id,
					youtube_title = title,
					youtube_duration = duration,
					station = station,
				)
				track.put()
				logging.info("New track put in the datastore.")
			
		# This is a Soundcloud track
		else:
			thumbnail = incoming["thumbnail"]
	
			# We check if the track is already owned by this station
			q = Track.all()
			q.filter("soundcloud_id", str(id))
			q.filter("station", station.key())
			track = q.get()
			
			if(track):
				logging.info("Track on Phonoblaster")
				
			# First time this track is submitted in this station
			else:
				logging.info("Track not on Phonoblaster")

				track = Track(
					soundcloud_id = str(id),
					soundcloud_title = title,
					soundcloud_duration = duration,
					soundcloud_thumbnail = thumbnail,
					station = station,
				)
				track.put()
				logging.info("New track put in the datastore.")
		
		return track
	
	@staticmethod
	def get_extended_tracks(tracks):
		extended_tracks = []
		for track in tracks:
			extended_track = Track.get_extended_track(track)
			extended_tracks.append(extended_tracks)
		return extended_tracks
	
	@staticmethod
	def get_extended_track(track):
		extended_track = {
			"track_id": str(track.key().id()),
			"track_created": timegm(track.created.utctimetuple()),
		}
		
		if(track.youtube_id):
			extended_track.update({
				"type": "youtube",
				"id": track.youtube_id,
				"title": track.youtube_title,
				"duration": track.youtube_duration,
				"thumbnail": "https://i.ytimg.com/vi/" + track.youtube_id + "/default.jpg",
			})
		else:
			extended_track.update({
				"type": "soundcloud",
				"id": track.soundcloud_id,
				"title": track.soundcloud_title,
				"duration": track.soundcloud_duration,
				"thumbnail": track.soundcloud_thumbnail,
			})
		
		return extended_track
	
	@staticmethod
	def number_of_views(track_id):
		shard_name = COUNTER_OF_VIEWS_PREFIX + str(track_id)
		count = Shard.get_count(shard_name)
		return count
	
	@staticmethod
	def increase_views_counter(track_id, value):
		shard_name = COUNTER_OF_VIEWS_PREFIX + str(track_id)
		Shard.increase(shard_name, value)
	
	@staticmethod
	def number_of_likes(track_id):
		shard_name = COUNTER_OF_LIKES_PREFIX + str(track_id)
		count = Shard.get_count(shard_name)
		return count
	
	@staticmethod
	def increment_likes_counter(track_id):
		shard_name = COUNTER_OF_LIKES_PREFIX + str(track_id)
		Shard.task(shard_name, "increment")
	
	@staticmethod
	def decrement_likes_counter(track_id):
		shard_name = COUNTER_OF_LIKES_PREFIX + str(track_id)
		Shard.task(shard_name, "decrement")
		
		