import logging
from calendar import timegm

from google.appengine.ext import db
from google.appengine.api.taskqueue import Task

from models.db.station import Station
from models.db.counter import Shard
from models.db.youtube import Youtube

COUNTER_OF_VIEWS_PREFIX = "track.views."
COUNTER_OF_FAVORITES_PREFIX = "track.favorites."

class Track(db.Model):
	"""
		youtube_id - ID of the track on Youtube
		youtube_title - String video title
		youtube_duration - Integer duration of the video in seconds
		youtube_music - Boolen, indicates if the video category is music or not
		station - 'owner' of the track
	"""
	
	youtube_id = db.StringProperty(required = True)
	youtube_title = db.StringProperty()
	youtube_duration = db.IntegerProperty()
	station = db.ReferenceProperty(Station, required = True, collection_name = "trackStation")
	created = db.DateTimeProperty(auto_now_add = True)

	@staticmethod
	def get_or_insert_by_youtube_id(broadcast, station):
		youtube_id = broadcast["youtube_id"]
		youtube_duration = broadcast["youtube_duration"]
		youtube_title = broadcast ["youtube_title"]
		
		track = None

		if(youtube_id):
			# We check if the track is already owned by this station
			q = Track.all()
			q.filter("youtube_id", youtube_id)
			q.filter("station", station.key())
			track = q.get()

			if(track):
				logging.info("Track on Phonoblaster")
				
			# First time this track is submitted in this station
			else:
				logging.info("Track not on Phonoblaster")

				track = Track(
					youtube_id = youtube_id,
					youtube_title = youtube_title,
					youtube_duration = youtube_duration,
					station = station,
				)
				track.put()
				logging.info("New track put in the datastore.")

		return track

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
	def number_of_favorites(track_id):
		shard_name = COUNTER_OF_FAVORITES_PREFIX + str(track_id)
		count = Shard.get_count(shard_name)
		return count
	
	@staticmethod
	def increment_favorites_counter(track_id):
		shard_name = COUNTER_OF_FAVORITES_PREFIX + str(track_id)
		Shard.task(shard_name, "increment")
	
	@staticmethod
	def decrement_favorites_counter(track_id):
		shard_name = COUNTER_OF_FAVORITES_PREFIX + str(track_id)
		Shard.task(shard_name, "decrement")
		
		