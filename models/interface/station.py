import logging
import os

from models.interface import config
from models.interface.user import InterfaceUser

from datetime import datetime
from datetime import timedelta
from random import randrange
from calendar import timegm
from time import gmtime

from models.db.track import Track
from models.db.station import Station
from models.db.user import User
from models.db.contribution import Contribution
from models.db.session import Session
from models.db.counter import *

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import channel

class InterfaceStation():
	
	def __init__(self, station_key = None, station_identifier = None):		
		# In most operations (add track, delete track), only the station key is provided
		if station_key:
			logging.info("Station proxy initialized with key")
			self.station_key = db.Key(str(station_key))
		# In other operations, we have the station identifier
		elif station_identifier:
			logging.info("Station proxy initialized with identifier")
			self.memcache_station_identifier_id = config.MEMCACHE_STATION_IDENTIFIER_PREFIX + str(station_identifier)
			self._station = memcache.get(self.memcache_station_identifier_id)
			
			if self._station is None:
				logging.info("Station not in memcache")
				self._station = Station.all().filter("identifier", station_identifier).get()
				
				if self._station:
					logging.info("Station exists")
					self.station_key = self._station.key()
					self.memcache_station_id = config.MEMCACHE_STATION_PREFIX + str(self.station_key.id())
					memcache.set_multi({
						self.memcache_station_identifier_id: self._station,
						self.memcache_station_id: self._station,			
					})
					logging.info("Station loaded TWICE in memcache (key and identifier)")
				else:
					self.station_key = None
					logging.info("Station does not exist")
			
			else:
				self.station_key = self._station.key()
				logging.info("Station in memcache")
			
		if(self.station_key):
			self.station_id = self.station_key.id()
			self.memcache_station_id = config.MEMCACHE_STATION_PREFIX + str(self.station_id)
			self.memcache_station_contributors_id = config.MEMCACHE_STATION_CONTRIBUTORS_PREFIX + str(self.station_id)
			self.memcache_station_tracklist_id = config.MEMCACHE_STATION_TRACKLIST_PREFIX + str(self.station_id)
			self.memcache_station_sessions_id = config.MEMCACHE_STATION_SESSIONS_PREFIX + str(self.station_id)	
	
	# Get the station
	@property
	def station(self):
		if not hasattr(self, "_station"):
			self._station = memcache.get(self.memcache_station_id)
			if self._station is None:
				logging.info("Station not in memcache")
				self._station = Station.get(self.station_key)
				if(self._station):
					logging.info("Station exists")
					self.memcache_station_identifier_id = config.MEMCACHE_STATION_IDENTIFIER_PREFIX + str(self._station.identifier)
					memcache.set_multi({
						self.memcache_station_id: self._station,
						self.memcache_station_identifier_id: self._station,
					})
					logging.info("Station loaded TWICE in memcache (key and identifier)")
				else:
					logging.info("Station does not exist")
			else:
				logging.info("Station already in memcache")	
		return self._station
	
	# Update the station information
	# PS: need to add more logic code in this... (instead of station/edit.py)
	def update_station(self, picture = None, thumbnail = None, identifier = None, website = None, description = None):
		# Necessary fields
		if picture:
			self.station.picture = picture
		if thumbnail:
			self.station.thumbnail = thumbnail
		
		# Unnecessary fields	
		self.station.website = website
		self.station.description = description
		
		# For identifier it's a little different ^^
		different_identifier = False
		if identifier:
			if(self.station.identifier == identifier):
				logging.info("Same identifier, no need to update memcache")
			else:
				logging.info("Different identifier, need to remove old value from memcache")
				old_memcache_station_identifier_id = self.memcache_station_identifier_id
				new_memcache_station_identifier_id = config.MEMCACHE_STATION_IDENTIFIER_PREFIX + str(identifier)
		
				self.station.identifier = identifier
				self.memcache_station_identifier_id = new_memcache_station_identifier_id
				different_identifier = True
		
		self.station.put()
		logging.info("New station information saved into datastore")
		
		memcache.set_multi({
			self.memcache_station_id: self.station,
			self.memcache_station_identifier_id: self.station,
		})
		logging.info("New station information saved TWICE into memcache")
		
		if(different_identifier):
			memcache.delete(old_memcache_station_identifier_id)
			logging.info("Old station value pointed by old identifier removed from memcache")
		
	
	# Update the station expiration time	
	def update_station_expiration_time(self, new_station_expiration_time):
		self.station.active = new_station_expiration_time
		self.station.put()
		logging.info("Station expiration time updated in datastore")

		self.memcache_station_identifier_id = config.MEMCACHE_STATION_IDENTIFIER_PREFIX + str(self.station.identifier)

		memcache.set_multi({
			self.memcache_station_id: self.station,
			self.memcache_station_identifier_id: self.station,
		})
		logging.info("Station expiration time updated TWICE in memcache (key and identifier)")
	
	# Get the station creator
	@property
	def station_creator(self):
		if not hasattr(self, "_station_creator"):
			creator_key = Station.creator.get_value_for_datastore(self.station)
			user_proxy = InterfaceUser(user_key = creator_key)
			self._station_creator = user_proxy.user
		return self._station_creator
	
	# Check if creator
	def is_creator(self, user_key):
		user_key = db.Key(str(user_key))
		station_creator_key = Station.creator.get_value_for_datastore(self.station)
		if(user_key == station_creator_key):
			return True
		else:
			return False
	
	# Get station contributors
	@property
	def station_contributors(self):
		if not hasattr(self, "_station_contributors"):
			self._station_contributors = memcache.get(self.memcache_station_contributors_id)

			if self._station_contributors is None:
				q = Contribution.all().filter("station", self.station_key)
				contributor_keys = [Contribution.contributor.get_value_for_datastore(c) for c in q.fetch(10)]
				self._station_contributors = set(db.get(contributor_keys))
				memcache.add(self.memcache_station_contributors_id, self._station_contributors)
				logging.info("Station contributors loaded in memcache")
			else:
				logging.info("Station contributors already in memcache")				

		return self._station_contributors
	
	# Add contributors to the station
	def add_contributors(self, applying_contributors):
		# Only keep new contributors
		new_contributors = set(applying_contributors).difference(self.station_contributors)
		new_contributions = []
		
		# Calculate the number of contributors left
		number_of_contributors_left = 10 - len(self.station_contributors)
		counter = 0
		
		for contributor in new_contributors:
			# If there are some contributors left, it's ok
			if(counter < number_of_contributors_left):
				contribution = Contribution(
					contributor = contributor.key(),
					station = self.station_key,
				)
				new_contributions.append(contribution)
				counter += 1
			# Otherwise, stop the loop
			else:
				break
		
		db.put(new_contributions)
		logging.info("New contributions saved in datastore")
		
		self.station_contributors.update(new_contributors)
		memcache.set(self.memcache_station_contributors_id, self.station_contributors)
		logging.info("Station contributors updated in memcache")
	
	# Delete a contributor from the station
	def delete_contributor(self, user_key, contribution_to_delete_key, contributor_to_delete_key):
		self.user_key = db.Key(str(user_key))
		
		# If user is the creator of the station
		station_creator_key = Station.creator.get_value_for_datastore(self.station)
		if(self.user_key == station_creator_key):
			logging.info("Allowed to delete contributors")
			
			contributors_left = set()
			for contributor in self.station_contributors:
				if(contributor.key() != contributor_to_delete_key):
					contributors_left.add(contributor)
			
			# If some modifications have been done
			if(len(contributors_left) != len(self.station_contributors)):
				# Delete contribution from datastore
				db.delete(contribution_to_delete_key)
				logging.info("Contribution removed from datastore")
				
				# Put contributors left in memcache
				memcache.set(self.memcache_station_contributors_id, contributors_left)
				logging.info("Contributors list updated in memcache")

				return True
			else:
				logging.info("No contributor found")
				return False
		else:
			logging.info("Not allowed to delete contributors")
			return False

	
	# Get the tracks currently in the station tracklist
	@property
	def station_tracklist(self):
		if not hasattr(self, "_station_tracklist"):
			self._station_tracklist = memcache.get(self.memcache_station_tracklist_id)
			
			if self._station_tracklist is None:
				q = Track.all()
				q.filter("station", self.station_key)
				q.filter("expired >", datetime.now())
				q.order("expired")
				self._station_tracklist = q.fetch(10)
				memcache.add(self.memcache_station_tracklist_id, self._station_tracklist)
				logging.info("Tracklist loaded in memcache")
			else:
				# We probably have to clean the memcache from old tracks
				cleaned_up_tracklist = []
				for track in self._station_tracklist:
					if(track.expired > datetime.now()):
						cleaned_up_tracklist.append(track)
				
				# We only update the memcache if some cleaning up was necessary
				if(len(self._station_tracklist) != len(cleaned_up_tracklist)):
					self._station_tracklist = cleaned_up_tracklist
					memcache.set(self.memcache_station_tracklist_id, self._station_tracklist)
					logging.info("Tracklist already in memcache and thus cleaned up")
				else:
					logging.info("Tracklist already in memcache and no need to clean up")

		return self._station_tracklist	
	
	# Add some tracks to the station tracklist
	def add_tracks(self, tracks, user_key):
		if(tracks):
			# If user is allowed to add
			if(self.is_allowed_to_add(user_key)):
				logging.info("User allowed to add in %s" %(self.station.identifier))
			
				room_in_tracklist = 10 - len(self.station_tracklist)
				# If the station queue has already 10 tracks it's full!
				if(room_in_tracklist == 0):
					logging.info("Tracklist full")
					return None
				# Otherwise, there is room for new tracks
				else:
					logging.info("Some room left in the tracklist")
					current_expiration_time = self.previous_expiration_time()
				
					# Shorten the number of tracks to the room in the tracklist
					tracks_to_add = tracks[:room_in_tracklist]
					logging.info(tracks_to_add)
				
					tracks_saved = []
					for track in tracks_to_add:
						current_expiration_time += timedelta(0,int(track["duration"]))
						new_track = Track(
							youtube_title = track["title"],
							youtube_id = track["id"],
							youtube_thumbnail_url = db.Link(track["thumbnail"]),
							youtube_duration = int(track["duration"]),
							station = self.station.key(),
							submitter = db.Key(str(user_key)),
							expired = current_expiration_time,
						)
						tracks_saved.append(new_track)
		
					# Save tracks in the datastore
					db.put(tracks_saved)
					logging.info("New tracks saved in the datastore")
		
					# Now the memcache
					self.station_tracklist += tracks_saved
					memcache.set(self.memcache_station_tracklist_id, self.station_tracklist)
					logging.info("Added to the station tracklist in memcache")
		
					# Update Station Expiration Time
					self.update_station_expiration_time(current_expiration_time)
		
					# Increment the station tracks counter by the right number
					self.increment_station_track_counter(len(tracks_saved))
		
					return tracks_saved

			else:
				return None
		else:
			return None
				
	# Check if user is allowed to add track to the station
	def is_allowed_to_add(self, user_key):
		user_key = db.Key(str(user_key))
		# If user is the creator of the station
		if(self.is_creator(user_key)):
			return True
		else:
			# If user is one of the contributor
			for contributor in self.station_contributors:
				if(user_key == contributor.key()):
					return True
			
			logging.info("User not allowed to add in %s station" %(self.station.identifier))
			return False
	
	# Returns the current station expiration time or the current time if there is no track in the tracklist
	def previous_expiration_time(self):
		if(len(self.station_tracklist) == 0):
			logging.info("Tracklist empty")
			return datetime.now()
		else:
			logging.info("Tracklist not empty")
			last_track = self.station_tracklist[-1]
			return last_track.expired
	
	# Increment the station tracks counter
	def increment_station_track_counter(self, value):
		counter_name = "tracks_counter_station_" + str(self.station_id)
		GeneralCounterShardConfig.bulk_increment(counter_name, value)
		logging.info("Station track counter incremented")
		
	# Delete a track from the station tracklist
	def delete_track(self, user_key, track_id):
		self.user_key = db.Key(user_key)
		
		# If the station_tracklist has at least 2 songs (given that the first one cannot be removed)
		if(len(self.station_tracklist) > 1):
			
			unchanged_tracks = []
			first_track = self.station_tracklist[0]
			tracks_to_edit = self.station_tracklist[1:]
			
			# self.station_tracklist is ordered by expiration time
			for track in self.station_tracklist[1:]:
				
				if(track.key().id() != int(track_id)):
					
					# Track must be be featured in the unchanged tracklist and be removed from the tracklist to edit
					unchanged_tracks.append(track)
					tracks_to_edit.remove(track)
				
				else:
					# We now have the track to delete. It must be removed from the tracklist to edit
					self.track_to_delete = track
					tracks_to_edit.remove(track)
					
					if(self.is_allowed_to_delete()):

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
						logging.info("Track %s removed from the datastore" %(soon_deleted_track_name))

						# We update the tracklist in the memcache (NB: the track_to_delete is not in this list)
						edited_tracklist = [first_track] + unchanged_tracks + tracks_edited
						memcache.set(self.memcache_station_tracklist_id, edited_tracklist)
						logging.info("Track removed and tracklist edited in memcache")

						# Update station expiration time
						self.update_station_expiration_time(new_station_expiration_time)

						# Decrement station track counter
						self.decrement_station_tracks_counter()

						return True

					else:
						return False
			
			logging.info("Track to delete has not been found")
			return False
		else:
			logging.info("Only one track in the tracklist. Impossible to remove anything")
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
	
	# Decrement the station tracks counter
	def decrement_station_tracks_counter(self):
		counter_name = "tracks_counter_station_" + str(self.station_id)
		GeneralCounterShardConfig.decrement(counter_name)
		logging.info("Station tracks counter decremented")
	
	
	# Get the number of sessions listening to the station
	@property
	def station_sessions(self):
		if not hasattr(self, "_station_sessions"):
			self._station_sessions = memcache.get(self.memcache_station_sessions_id)
			
			if self._station_sessions is None:
				# Retrieve the number of non expired sessions (but we don't know yet if they have been confirmed...)
				q = Session.all()
				q.filter("station", self.station_key)
				q.filter("ended", None)
				q.filter("created >", datetime.now() - timedelta(0,7200))
				"""
				self._station_sessions = q.fetch(100)
				"""
				
				# In theory there could be max 111 sessions (100 listeners + 10 contributors + 1 creator) but I fetch more in case...
				candidate_sessions = q.fetch(200)
				self._station_sessions = []
				for session in candidate_sessions:
					# The session has been confirmed
					if(session.updated):
						self._station_sessions.append(session)
				
				# Put it in memcache
				memcache.add(self.memcache_station_sessions_id, self._station_sessions)
				logging.info("Sessions loaded in memcache")
			
			else:
				# We probably have to clean up this sessions list
				cleaned_up_sessions_list = []
				limit = datetime.now() - timedelta(0,7200)
				
				for session in self._station_sessions:
					if(session.created > limit):
						cleaned_up_sessions_list.append(session)
				
				if(len(cleaned_up_sessions_list) != len(self._station_sessions)):
					self._station_sessions = cleaned_up_sessions_list
					memcache.set(self.memcache_station_sessions_id, self._station_sessions)
					logging.info("Sessions list already in memcache and cleaned up")
				else:
					logging.info("Sessions list already in memcache but no need to clean up")
				
		return self._station_sessions
	
	# Add a session
	def add_session(self, user_key = None):
		new_session = None
		station_sessions = self.station_sessions
		
		# We retrieve the latest sessions whose channel API token is not expired (3600 sec ~ 1h) / NB: tokens expired after 2 hours
		q = Session.all()
		q.filter("created >", datetime.now() - timedelta(0,3600))
		q.filter("station", self.station_key)
		# 200 is arbitrary
		last_sessions = q.fetch(200)
		
		for session in last_sessions:
			# Session already ended + Token still available => we reuse it
			# Session never confirmed + Token created more than 5 ago => we reuse it
			# NB: it would have been cool to do this test in the query but app engine does not allow more than one inequality filter...
						
			# Session already ended + Token still available => we reuse it
			if(session.ended !=None):
				new_session = session
				logging.info("We reuse an old channel_id and token because this session already ended")			
				
				# We completly reset this session
				new_session.updated = None
				new_session.ended = None
			
			# Session never confirmed + Token created more than 5 minutes ago => we reuse it
			if(session.updated == None and session.created < datetime.now() - timedelta(0,300)):
				new_session = session
				logging.info("We reuse an old channel_id and token because this session has never been confirmed")
			
			if(new_session):	
				new_session.user = user_key
				new_session.put()
				logging.info("New station session saved in datastore. To put in memcache after client connection")
				
				return new_session
			
			
			"""
			if(session.ended != None):
				new_session = session
				logging.info("We reuse an old channel_id and token")			
				
				new_session.ended = None
				new_session.user = user_key
				new_session.put()
				logging.info("New station session saved in datastore")
				
				# Put it in the memcache
				station_sessions.append(new_session)
				memcache.set(self.memcache_station_sessions_id, station_sessions)
				logging.info("Station sessions list updated in memcache")
				
				return new_session
			"""
		
		if not(new_session):
			logging.info("There is no old channel_id or token to reuse")
			time_now = str(timegm(gmtime()))
			random_integer = str(randrange(1000))
			
			new_channel_id = time_now + random_integer
			new_channel_token = channel.create_channel(new_channel_id)
			
			new_session = Session(
				channel_id = new_channel_id,
				channel_token = new_channel_token,
				station = self.station_key,
				user = user_key,
			)
			new_session.put()
			logging.info("New station session saved in datastore. To put in memcache after client connection")
			
			"""
			logging.info("New station session saved in datastore.")
			
			# Put it in memcache
			station_sessions.append(new_session)
			memcache.set(self.memcache_station_sessions_id, station_sessions)
			logging.info("Station sessions list updated in memcache")
			"""
			
			return new_session
	
	# Confirm a session (a client has requested a token and has connected to the channel)
	# Not efficient, seems to require a refactoring.... 
	def confirm_session(self, session_to_confirm):
		station_sessions = self.station_sessions

		# Put an updated date in the session entity
		session_to_confirm.updated = datetime.now()
		session_to_confirm.put()
		logging.info("Session to confirm saved in the datastore")

		# Add the station confirmed to the memcache
		station_sessions.append(session_to_confirm)
		memcache.set(self.memcache_station_sessions_id, station_sessions)
		logging.info("Station sessions list updated in memcache")	
			
	# End a session
	# Not efficient seems to require a refactoring.... (should only provide the channel_id)
	def end_session(self, ending_session):
		old_sessions_list = self.station_sessions
		
		# Put an end to the session in the datastore
		ending_session.ended = datetime.now()
		ending_session.put()
		logging.info("Session ended in the datastore")
		
		# Remove this station from the datastore
		new_sessions_list = old_sessions_list
		for session in old_sessions_list:
			if(session.key() == ending_session.key()):
				new_sessions_list.remove(session)
		memcache.set(self.memcache_station_sessions_id, new_sessions_list)
		logging.info("Station sessions list updated in memcache")
				

			
		