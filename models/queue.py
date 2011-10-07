import logging

from datetime import datetime
from datetime import timedelta
from random import randrange

from db.track import Track
from db.station import Station
from db.session import Session

from notifiers.track import TrackNotifier

from google.appengine.ext import db

class Queue():
	
	def __init__(self, station_key):
		self.station = Station.get(station_key)
	
	def getTracks(self):
		query = Track.all()
		query.filter("station", self.station.key())
		query.filter("expired >", datetime.now())
		query.order("expired")
		
		tracks = query.fetch(10)
		
		return tracks
	
	@property
	def numberOfTracks(self):
		query = Track.all()
		query.filter("station", self.station.key())
		query.filter("expired >", datetime.now())
		query.order("expired")
		number = query.count()		
		return number
	
	def addTrack(self, title, id, thumbnail, duration, user_key):
		tracks = self.getTracks()
		if(len(tracks) == 10):
			return None
		else:
			expiration_interval = timedelta(0,int(duration))
			
			if(len(tracks) == 0):
				expiration_time = datetime.now() + expiration_interval
			else:
				last_track = tracks[-1]
				expiration_time = last_track.expired + expiration_interval

			newTrack = Track(
				youtube_title = title,
				youtube_id = id,
				youtube_thumbnail_url = db.Link(thumbnail),
				youtube_duration = int(duration),
				station = self.station.key(),
				submitter = user_key,
				expired = expiration_time,
			)
			newTrack.put()
	
			logging.info("New track %s in the %s tracklist" %(title, self.station.identifier))
			
			return newTrack

	def shuffle(self, user_key):
		latest_tracks = Track.all().filter("submitter", user_key).order("-added").fetch(50)
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
		
		return random_tracks
	
	def deleteTrack(self, track_key):
		track_to_delete = Track.get(track_key)
		if(track_to_delete):
			track_beginning = track_to_delete.expired - timedelta(0,track_to_delete.youtube_duration)
			#The track is not currenlty being played
			if(track_beginning > datetime.now()):
				tracks_to_edit = Track.all().filter("station", self.station.key()).filter("expired >", track_to_delete.expired)

				tracks_edited = []
				offset = timedelta(0, track_to_delete.youtube_duration)
				for track in tracks_to_edit:
					track.expired -= offset
					tracks_edited.append(track)
				
				db.put(tracks_edited)
				logging.info("Next tracks edited")
				
				soon_deleted_track_name = track_to_delete.youtube_title
				track_to_delete.delete()
				logging.info("Track %s removed from database" %(soon_deleted_track_name))

				return True
			
			#It's not possible to remove a track currently being played
			else:
				return False
		else:
			return False
			
			
			
		