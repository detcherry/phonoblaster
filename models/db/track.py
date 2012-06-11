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
	def get_or_insert_by_youtube_id(incoming, station):
		youtube_id = incoming["youtube_id"]
		youtube_duration = incoming["youtube_duration"]
		youtube_title = incoming["youtube_title"]
		
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
	def get_extended_track(track):
		return Track.get_extended_tracks([track])[0]

	@staticmethod
	def get_extended_tracks(tracks):
		extended_tracks = [
			{
				"track_id": track.key().id(),
				"track_created": timegm(track.created.utctimetuple()),
				"youtube_id": track.youtube_id,
				"youtube_title": track.youtube_title,
				"youtube_duration": track.youtube_duration,
			} for track in tracks]

		return extended_tracks

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
		
		