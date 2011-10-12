import logging
import os

from datetime import datetime
from datetime import timedelta
from random import randrange

from db.track import Track
from db.station import Station
from db.user import User
from db.contribution import Contribution
from db.counter import *

from google.appengine.ext import db
from google.appengine.api import memcache

class Queue():
	
	def __init__(self, station_key):
		self.station = Station.get(station_key)
	
	# Get the tracks currently in the station tracklist
	def get_tracks(self):
		memcache_id = os.environ["CURRENT_VERSION_ID"] + "_tracklist_station_" + str(self.station.key().id())
		tracks = memcache.get(memcache_id)
		
		if tracks is None:
			q = Track.all()
			q.filter("station", self.station.key())
			q.filter("expired >", datetime.now())
			q.order("expired")
			tracks = q.fetch(10)
			memcache.add(memcache_id, tracks)
			logging.info("Tracklist loaded in memcache")
		else:
			# We probably have to clean the memcache from old tracks
			for track in tracks:
				if(track.expired <= datetime.now()):
					tracks.remove(track)
			memcache.set(memcache_id, tracks)
			logging.info("Tracklist already in memcache and thus cleaned up")
		
		return tracks
	
	# Add a new track to the station tracklist
	def add_track(self, title, id, thumbnail, duration, user_key):
		self.user_key = db.Key(user_key)
		
		# If user is allowed to add
		if(self.is_allowed_to_add()):
			logging.info("User allowed to add")
			self.station_tracklist = self.get_tracks()
			
			# If the station queue has already 10 tracks it's full!
			if(len(self.station_tracklist) == 10):
				logging.info("Tracklist full")
				return None
				
			# Otherwise, there is room for new tracks
			else:
				logging.info("Some room left in the tracklist")
				self.calculate_track_expiration_time(duration)
				
				# Save new track to the datastore
				new_track = Track(
					youtube_title = title,
					youtube_id = id,
					youtube_thumbnail_url = db.Link(thumbnail),
					youtube_duration = int(duration),
					station = self.station.key(),
					submitter = self.user_key,
					expired = self.new_track_expiration_time,
				)
				new_track.put()
				logging.info("New track %s in the %s tracklist saved in the datastore" %(title, self.station.identifier))
				
				# Add track to the memcache 
				self.station_tracklist.append(new_track)
				memcache_id = os.environ["CURRENT_VERSION_ID"] + "_tracklist_station_" + str(self.station.key().id())
				memcache.set(memcache_id, self.station_tracklist)
				logging.info("Updated in memcache")				
				
				# Update Station Expiration Time
				self.update_station_expiration_time(self.new_track_expiration_time)
				
				# Increment Station Track Counter
				self.increment_station_track_counter()
				
				return new_track
		else:
			return None		
	
	# Check if user is allowed to add track to the station
	def is_allowed_to_add(self):
		# If user is the creator of the station
		station_creator_key = Station.creator.get_value_for_datastore(self.station)
		if(self.user_key == station_creator_key):
			return True
		else:
			# If user is one of the contributor
			contribution = Contribution.all().filter("station", self.station.key()).filter("contributor", self.user_key).get()
			if(contribution):
				return True
			
			logging.info("User not allowed to add")
			return False
	
	# Calculate the expiration time of the track being added
	def calculate_track_expiration_time(self, duration):
		expiration_interval = timedelta(0,int(duration))
		if(len(self.station_tracklist) == 0):
			self.new_track_expiration_time = datetime.now() + expiration_interval
		else:
			last_track = self.station_tracklist[-1]
			self.new_track_expiration_time = last_track.expired + expiration_interval
	
	# Increment the station tracks counter
	def increment_station_track_counter(self):
		counter_name = "tracks_counter_station_" + str(self.station.key().id())
		GeneralCounterShardConfig.increment(counter_name)
		logging.info("Station track counter incremented")
	
	# Update the station expiration time	
	def update_station_expiration_time(self, new_station_expiration_time):
		self.station.active = new_station_expiration_time
		self.station.put()
		logging.info("Station expiration time updated")
	
	# Delete a track from the station tracklist
	def delete_track(self, user_key, track_id):
		self.track_to_delete = Track.get_by_id(int(track_id))
		self.user_key = db.Key(user_key)
		
		if(self.track_to_delete):
			if(self.is_allowed_to_delete()):
				if(self.is_currently_being_played()):
					return False
				else:					
					# New code
					tracklist = self.get_tracks()
					
					limit = self.track_to_delete.expired
					unchanged_tracks = []
					tracks_to_edit = []
					# Browse the tracklist and see which tracks need to be updated 
					for track in tracklist:
						# If the expiration time is more, the tracks needs to be updated
						if(track.expired > limit):
							tracks_to_edit.append(track)
						# If the expiration time is less, it's ok
						elif(track.expired < limit):
							unchanged_tracks.append(track)
						#if track.expired == limit it's the track_to_delete

					tracks_edited = []
					self.expiration_offset = timedelta(0, self.track_to_delete.youtube_duration)
					for track in tracks_to_edit:
						track.expired -= self.expiration_offset
						tracks_edited.append(track)
					
					if(tracks_edited):
						# We save the edited tracks to the datastore
						db.put(tracks_edited)
						logging.info("Next tracks edited")
						# We update the station expiration time with the last edited track
						new_station_expiration_time = tracks_edited[-1].expired
					else:
						# We update the station expiration time with the beginning of the track that is going to be deleted
						new_station_expiration_time = self.track_to_delete.expired - timedelta(0,self.track_to_delete.youtube_duration)

					# We remove the track from the datastore
					soon_deleted_track_name = self.track_to_delete.youtube_title
					self.track_to_delete.delete()
					logging.info("Track %s removed from %s tracklist in the datastore" %(soon_deleted_track_name, self.station.identifier))
					
					# We update the tracklist in the memcache (NB: the track_to_delete is not in this list)
					edited_tracklist = unchanged_tracks + tracks_edited
					memcache_id = os.environ["CURRENT_VERSION_ID"] + "_tracklist_station_" + str(self.station.key().id())
					memcache.set(memcache_id, edited_tracklist)
					logging.info("Track removed from memcache")
					
					# Update station expiration time
					self.update_station_expiration_time(new_station_expiration_time)
					
					# Decrement station track counter
					self.decrement_station_tracks_counter()
					
					return True
			else:
				return False
		else:
			return False
	
	# Check if the user is allowed to delete the track
	def is_allowed_to_delete(self):
		# If the user has submitted the track, he's allowed to delete it
		track_submitter_key = Track.submitter.get_value_for_datastore(self.track_to_delete)
		if(self.user_key == track_submitter_key):
			logging.info("Allowed to delete the track")
			return True
		else:
			logging.info("Not allowed to delete the track")
			return False
			
	# Check if the track to be deleted is being currently played
	def is_currently_being_played(self):
		track_beginning = self.track_to_delete.expired - timedelta(0,self.track_to_delete.youtube_duration)
		# If the track is not currently being played
		if(track_beginning > datetime.now()):
			logging.info("Track not currently being played")
			return False
		else:
			logging.info("Track currently being played")
			return True
	
	# Decrement the station tracks counter
	def decrement_station_tracks_counter(self):
		counter_name = "tracks_counter_station_" + str(self.station.key().id())
		GeneralCounterShardConfig.decrement(counter_name)
		logging.info("Station tracks counter decremented")
	
	
	
	
	
	
	
	
	
	"""
		Deprecated functions
		TO BE REMOVE SOON 
	"""
	
	def getTracks(self):
		query = Track.all()
		query.filter("station", self.station.key())
		query.filter("expired >", datetime.now())
		query.order("expired")
		
		tracks = query.fetch(10)
		
		return tracks

	def shuffle(self, user_key):
		latest_tracks = Track.all().filter("submitter", user_key).order("-added").fetch(100)
		number_of_latest_tracks = len(latest_tracks)
		non_expired_tracks = self.getTracks()
		number_of_remaining_tracks = 10 - len(non_expired_tracks)
		
		#Existing Youtube videos that are in the station tracklist (non expired)
		existing_track_ids = []
		for track in non_expired_tracks:
			existing_track_ids.append(track.youtube_id)
					
		random_tracks = []
		
		#If the user has already shared tracks on phonoblaster
		if(number_of_latest_tracks > 0):
			
			#Initialization of the latest track expiration time
			if(number_of_remaining_tracks == 10):
				latest_track_expiration_time = datetime.now()
			else:
				latest_track_expiration_time = non_expired_tracks[-1].expired
			
			#We try to put in the buffer as many songs as possible
			for i in range(0, number_of_remaining_tracks):
				
				#We picked a random track among the latest tracks shared by the user
				random_integer = randrange(number_of_latest_tracks)
				random_track = latest_tracks[random_integer]
				if(random_track.youtube_id in existing_track_ids):
					logging.info("Track already shuffled or in the tracklist")
				
				#If the song is not already in the tracklist
				else:
					track_added = Track(
						youtube_title = random_track.youtube_title,
						youtube_id = random_track.youtube_id,
						youtube_thumbnail_url = random_track.youtube_thumbnail_url,
						youtube_duration = random_track.youtube_duration,
						station = self.station.key(),
						submitter = user_key,
						expired = latest_track_expiration_time + timedelta(0, random_track.youtube_duration),
					)
					logging.info("Track shuffled: %s" % (track_added.youtube_title))
					latest_track_expiration_time = track_added.expired
					random_tracks.append(track_added)
					existing_track_ids.append(track_added.youtube_id)
		
		if(random_tracks):
			db.put(random_tracks)
			logging.info("Tracks shuffled saved as well")
		
		#Increment the tracks counter
		counter_name = "tracks_counter_station_" + str(self.station.key().id())
		for i in range(len(random_tracks)):
			GeneralCounterShardConfig.increment(counter_name)
		
		return random_tracks
			
	def getRecentHistory(self,num):
		query = Track.all()
		query.filter("station",self.station.key())
		query.filter("expired <", datetime.now())
		query.order("-expired")

		tracks = query.fetch(num)

		return tracks	
		