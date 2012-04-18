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
	def get_extended_tracks(tracks):
		"""
			Returns a list of extended tracks - (Possibly None)
		"""
		
		extended_tracks = []
		youtube_ids = []
		
		if(tracks):
			for track in tracks:
				youtube_ids.append(track.youtube_id)
		
			youtube_tracks = Youtube.get_extended_tracks(youtube_ids) #TO BE REMOVED

			for track, youtube_track in zip(tracks, youtube_tracks):
				if(youtube_track):
					extended_tracks.append({
						"track_id": track.key().id(),
						"track_created": timegm(track.created.utctimetuple()),
						"youtube_id": youtube_track["id"],
						"youtube_title": youtube_track["title"],
						"youtube_duration": youtube_track["duration"],
					})
				else:
					extended_tracks.append(None)

		return extended_tracks

	@staticmethod
	def get_or_insert_by_youtube_id(youtube_id, station):
		track = None
		extended_track = None

		if(youtube_id):
			# We check if the track is already owned by this station
			q = Track.all()
			q.filter("youtube_id", youtube_id)
			q.filter("station", station.key())
			track = q.get()

			if(track):
				logging.info("Track on Phonoblaster")
				extended_track = Track.get_extended_tracks([track])[0]

			# First time this track is submitted in this station
			else:
				logging.info("Track not on Phonoblaster")
				youtube_track = Youtube.get_extended_tracks([youtube_id])[0] # TO BE REMOVED

				# If track on Youtube, save the track on Phonoblaster, generate the extended track
				if(youtube_track):
					logging.info("Track on Youtube")
					track = Track(
						youtube_id = youtube_id,
						station = station,
					)
					track.put()
					logging.info("New track put in the datastore.")

					extended_track = {
						"track_id": track.key().id(),
						"track_created": timegm(track.created.utctimetuple()),
						"youtube_id": youtube_track["id"],
						"youtube_title": youtube_track["title"],
						"youtube_duration": youtube_track["duration"],
					}

		return (track, extended_track)

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
		
		